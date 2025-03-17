import os
import os.path as op
import argparse
from stress_risk.utils.data import Subject
import numpy as np
from braincoder.utils import get_rsq
import pandas as pd
from nilearn.maskers import NiftiMasker
from nilearn import image
from braincoder.models import RegressionGaussianPRF


# concatenate sessions paradigms with additional column 'range'
# make mu dependent on range(session) but eveything else fix?

# be consistent to Gilles 'neural_priors' project 
# (for which he orginally implemented the RegressionGaussianPRF in braincoder)

# MODEL 0: NULL MODEL
# MODEL 1: Shift model
# MODEL 2: Everything differs-model

def get_model(paradigm, model_label):
    if model_label == 0:
        regressors = {}
    elif model_label == 1:
        regressors = {'mu':'0 + C(session)'}
    elif model_label == 2:
        regressors = {'mu':'0 + C(session)',
                      'sd': '0 + C(session)',
                      'amplitude': '0 + C(session)',
                      'baseline': '0 + C(session)'}
    else:
        raise NotImplementedError(f"Model {model_label} is not implemented")

    model = RegressionGaussianPRF(paradigm=paradigm, regressors=regressors)

    return model

def get_grid(model_label):
    modes = np.linspace(np.log(5), np.log(40), 30)
    sds = np.linspace(np.log(2), np.log(30), 30)
    amplitudes = np.array([1.], dtype=np.float32)
    baselines = np.array([0], dtype=np.float32)

    if model_label == 0:
        return modes, sds, amplitudes, baselines
    elif model_label == 1:
        return modes, modes, sds, amplitudes, baselines
    elif model_label == 2:
        return modes, modes, sds, sds, amplitudes, amplitudes, baselines, baselines
    else:
        raise NotImplementedError(f"Model {model_label} is not implemented")

def fit_model(model_label, model, data, paradigm, max_n_iterations=1000):
    from braincoder.optimize import ParameterFitter
    fitter = ParameterFitter(model, data, paradigm)

    grid = get_grid(model_label)

    grid_pars = fitter.fit_grid(*grid, use_correlation_cost=True)
    if model_label in[0, 1]:
        init_pars = fitter.refine_baseline_and_amplitude(grid_pars, n_iterations=2)
    elif model_label in [2]:
        fixed_pars = [('mu_unbounded', 'C(session)[1]'), ('mu_unbounded', 'C(session)[2]'), ('sd_unbounded', 'C(session)[1]'), ('sd_unbounded', 'C(session)[2]')]
        init_pars = fitter.fit(init_pars=grid_pars, learning_rate=.05, store_intermediate_parameters=False, max_n_iterations=max_n_iterations, r2_atol=0.00001, fixed_pars=fixed_pars)

    gd_pars = fitter.fit(init_pars=init_pars, learning_rate=.05, store_intermediate_parameters=False, max_n_iterations=max_n_iterations, r2_atol=0.00001)

    return gd_pars

def get_conditionspecific_parameters(model_label, model, estimated_parameters):
    
    conditions = pd.DataFrame({'x':[0,0], 'session':[1,2]}, index=pd.Index([1, 2], name='session'))

    pars = model.get_conditionspecific_parameters(conditions, estimated_parameters)
    
    return pars.unstack('session')

def main(subject, smoothed, model_label=1, bids_folder='/data/ds-stressrisk', retroicor=True, debug=False, roi='NPC_R'): # gaussian=True, 

    max_n_iterations = 100 if debug else 1000

    sub = Subject(subject,bids_folder=bids_folder)
    subject = f'{int(subject):02d}'

    source_key_glm = 'glm_stim1.denoise'

    source_key_vselect = 'encoding_model.cv.denoise'
    target_key = 'encoding_model'
    target_key += f'.model{model_label}'
    
    if retroicor:
        target_key += '.retroicor'
        source_key_glm += '.retroicor'
        source_key_vselect += '.retroicor'

    if smoothed:
        source_key_glm += '.smoothed'
        target_key += '.smoothed'
        source_key_vselect += '.smoothed'

    target_dir = op.join(bids_folder, 'derivatives', target_key, f'sub-{subject}', 'func')
    if not op.exists(target_dir):
        os.makedirs(target_dir)

    # Get paradigm/data/model
    sub = Subject(subject, bids_folder=bids_folder)
    behavior = sub.get_behavior(sessions=None, drop_no_responses=False).reset_index('session') # session will be range
    paradigm = behavior[['n1', 'session']].rename(columns={'n1':'x' }) #,'session':'range'
    #if not gaussian:
    paradigm['x'] = np.log(paradigm['x']) # as before
    paradigm['x'] = paradigm['x'].astype(np.float32)
    print(paradigm.describe())

    # get average cv-r2 map from seesion 1 for voxel selection
    session1 = 1
    ips_mask = sub.get_volume_mask(roi=roi, session=1, epi_space=True) # anat from session1
    ips_masker = NiftiMasker(mask_img=ips_mask)
    # single trial functional brain data
    data_s1 = op.join(bids_folder, 'derivatives', source_key_glm,
                    f'sub-{subject}', f'ses-1', 'func', f'sub-{subject}_ses-1_task-risk_space-T1w_desc-stims1_pe.nii.gz')
    data_s2 = op.join(bids_folder, 'derivatives', source_key_glm,
                    f'sub-{subject}', f'ses-2', 'func', f'sub-{subject}_ses-2_task-risk_space-T1w_desc-stims1_pe.nii.gz')
    data = np.concatenate([ips_masker.fit_transform(data_s1), ips_masker.fit_transform(data_s2)], axis=0)
    data = pd.DataFrame(data, index=paradigm.index)

    # # Get model
    model = get_model(paradigm, model_label)

    # # Fit model
    gd_pars = fit_model(model_label, model, data, paradigm, max_n_iterations=max_n_iterations)

    pred = model.predict(parameters=gd_pars, paradigm=paradigm)
    r2 = get_rsq(data, pred)
    print(r2.describe())

    conditionwise_pars = get_conditionspecific_parameters(model_label, model, gd_pars)
    print(conditionwise_pars)

    # # save output

    ips_masker.inverse_transform(r2).to_filename(op.join(target_dir, f'sub-{subject}_desc-r2.optim_space-T1w_pars.nii.gz'))

    for par in ['mu', 'sd', 'amplitude', 'baseline']:
        for session in range(1, 3):
            target_fn = op.join(target_dir, f'sub-{subject}_ses-{session}_desc-{par}.optim_space-T1w_pars.nii.gz')
            ips_masker.inverse_transform(conditionwise_pars[par, session]).to_filename(target_fn)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('subject', type=str)
    parser.add_argument('--model_label', default=1, type=int)
    parser.add_argument('--bids_folder', default='/data/ds-stressrisk')
    parser.add_argument('--smoothed', action='store_true')
    #parser.add_argument('--log_space', action='store_true')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    main(args.subject, model_label=args.model_label, smoothed=args.smoothed, bids_folder=args.bids_folder, debug=args.debug) # , gaussian=not args.log_space
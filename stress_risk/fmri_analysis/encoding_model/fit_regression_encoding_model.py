import os
import os.path as op
import argparse
from stress_risk.utils.data import Subject
import numpy as np
from braincoder.utils import get_rsq
import pandas as pd
from models_sessionRegressor import get_paradigm, get_model, fit_model, get_conditionspecific_parameters
from nilearn.maskers import NiftiMasker
from nilearn import image

# concatenate sessions paradigms with additional column 'range'
# make mu dependent on range(session) but eveything else fix?

# be consistent to Gilles 'neural_priors' project 
# (for which he orginally implemented the RegressionGaussianPRF in braincoder)

def main(subject, smoothed, model_label=6, bids_folder='/Users/mrenke/data/ds-stressrisk', retroicor=True, debug=False, roi='NPC_R'): # gaussian=True, 

    max_n_iterations = 100 if debug else 1000

    sub = Subject(subject,bids_folder=bids_folder)
    subject = f'{int(subject):02d}'

    regressor_name = 'session'
    if model_label == 6: ## this! -- we dont have a prediction on how exaclty the mu changes! 
        regressors = {'mu':f'0 + C({regressor_name})'}
    else: 
        raise NotImplementedError(f"Model {model_label} is not implemented")
    
    source_key_glm = 'glm_stim1.denoise'
    source_key_vselect = 'encoding_model.cv.denoise'
    target_key = 'encoding_model'
    target_key += f'.model{model_label}'
    
    if retroicor:
        target_key += '.retroicor'
        source_key_glm += '.retroicor'
        source_key_vselect += '.retroicor'

    target_dir = op.join(bids_folder, 'derivatives', target_key, f'sub-{subject}', 'func')
    if not op.exists(target_dir):
        os.makedirs(target_dir)

    # Get paradigm/data/model
    sub = Subject(subject, bids_folder=bids_folder)
    behavior = sub.get_behavior(sessions=None).reset_index('session') # session will be range
    paradigm = behavior[['n1', 'session']].rename(columns={'n1':'x' }) #,'session':'range'
    #if not gaussian:
    paradigm['x'] = np.log(paradigm['x']) # as before
    paradigm['x'] = paradigm['x'].astype(np.float32)
    print(paradigm.describe())

    # get average cv-r2 map from seesion 1 for voxel selection
    session1 = 1
    ips_mask = sub.get_volume_mask(roi=roi, session=1, epi_space=True) # anat from session1
    ips_masker = NiftiMasker(mask_img=ips_mask)
    im_cvr2_fn = op.join(bids_folder, 'derivatives', source_key_vselect, f'sub-{subject}', f'ses-{session1}','func', f'sub-{subject}_ses-{session1}_desc-cvr2.optim_space-T1w_pars.nii.gz')
    im_cvr2 = image.load_img(im_cvr2_fn)
    cv_r2 = pd.DataFrame(ips_masker.fit_transform(im_cvr2))
    r2_mask = cv_r2 > 0.0
    r2_mask = r2_mask.to_numpy().T
    masker = NiftiMasker(mask_img=r2_mask)
    n_voxels = r2_mask.sum()
    print(f'Number of voxels: {n_voxels}')

    # single trial functional brain data
    data_s1 = op.join(bids_folder, 'derivatives', source_key_glm,
                    f'sub-{subject}', f'ses-1', 'func', f'sub-{subject}_ses-1_task-risk_space-T1w_desc-stims1_pe.nii.gz')
    data_s2 = op.join(bids_folder, 'derivatives', source_key_glm,
                    f'sub-{subject}', f'ses-2', 'func', f'sub-{subject}_ses-2_task-risk_space-T1w_desc-stims1_pe.nii.gz')
    data = np.concatenate([ips_masker.fit_transform(data_s1), ips_masker.fit_transform(data_s2)], axis=0)
    data = pd.DataFrame(data, index=paradigm.index)

    # Get model
    from braincoder.models import RegressionGaussianPRF
    #model = get_model(paradigm, model_label, gaussian=gaussian)
    model = RegressionGaussianPRF(paradigm=paradigm, regressors=regressors) # should match with sesssion as regressor!

    # Fit model
    from models_sessionRegressor import fit_model #, get_conditionspecific_parameters
    pars = fit_model(model, paradigm, data, model_label, max_n_iterations=max_n_iterations)
    pred = model.predict(parameters=pars, paradigm=paradigm)
    r2 = get_rsq(data, pred)

    # save output
    target_fn = op.join(target_dir, f'sub-{subject}_desc-r2.optim_space-T1w_pars.npy')
    np.save(target_fn, np.array(r2))
    #pars = get_conditionspecific_parameters(model_label, model, pars, gaussian=gaussian)
    parameters = pars.copy()

    conditions = pd.DataFrame({'x':[0,0], regressor_name:[0,1]}, index=pd.Index(['1', '2'], name=regressor_name))
    design_matrices = model.build_design_matrices(conditions,regressors=regressors ) #cond = paradigm ?
    if hasattr(parameters, 'values'):
        parameters_ = parameters.values
    else:
        parameters_ = np.array(parameters)
    parameters_ = parameters_[np.newaxis, ...]
    transformed_parameters = model._get_base_parameters(design_matrices, parameters_).numpy()
    transformed_parameters = np.reshape(transformed_parameters, (-1, transformed_parameters.shape[-1]))
    transformed_parameters = pd.DataFrame(transformed_parameters,
                                index=pd.MultiIndex.from_product([conditions.index, parameters.index]),
                                columns=model.base_parameter_labels)
    for regres_vars, values in transformed_parameters.groupby(regressor_name):
        for par, value in values.T.iterrows():
            target_fn = op.join(target_dir, f'sub-{subject}_desc-{par}.{regres_vars}.optim_space-T1w_pars.npy')
            #masker.inverse_transform(value).to_filename(target_fn)
            np.save(target_fn, np.array(value))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('subject', type=str)
    parser.add_argument('--model_label', default=6, type=int)
    parser.add_argument('--bids_folder', default='/Users/mrenke/data/ds-stressrisk')
    parser.add_argument('--smoothed', action='store_true')
    parser.add_argument('--log_space', action='store_true')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    main(args.subject, model_label=args.model_label, smoothed=args.smoothed, bids_folder=args.bids_folder, debug=args.debug, gaussian=not args.log_space)
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
from fit_regression_encoding_model import get_model, fit_model, get_conditionspecific_parameters


# concatenate sessions paradigms with additional column 'range'
# make mu dependent on range(session) but eveything else fix?

# be consistent to Gilles 'neural_priors' project 
# (for which he orginally implemented the RegressionGaussianPRF in braincoder)

# MODEL 0: NULL MODEL
# MODEL 1: Shift model

def main(subject, smoothed, model_label=1, bids_folder='/data/ds-stressrisk', retroicor=True, debug=False, roi='NPC_R'): # gaussian=True, 

    max_n_iterations = 100 if debug else 1000

    sub = Subject(subject,bids_folder=bids_folder)
    subject = f'{int(subject):02d}'

    source_key_glm = 'glm_stim1.denoise'

    source_key_vselect = 'encoding_model.cv.denoise'
    target_key = 'encoding_model.cv'
    target_key += f'.model{model_label}'
    
    if retroicor:
        target_key += '.retroicor'
        source_key_glm += '.retroicor'
        source_key_vselect += '.retroicor'

    if smoothed:
        source_key_glm += '.smoothed'

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
    paradigm.set_index('session', drop=False, inplace=True, append=True)
    print(paradigm)
    paradigm = paradigm.droplevel('subject').reorder_levels(['session', 'run', 'trial_nr']).sort_index()
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

    print(data)

    all_cvr2 = []

    for (test_session, test_run), _ in paradigm.groupby(level=['session', 'run']):

        print(f'Fitting using session {test_session} run {test_run} as test set')

        test_data, test_paradigm = data.loc[(test_session, test_run)].copy().astype(np.float32), paradigm.loc[(test_session, test_run)].copy().astype(np.float32)
        train_data, train_paradigm = data.drop((test_session, test_run)).copy(), paradigm.drop((test_session, test_run)).copy()

        # Get model
        model = get_model(train_paradigm, model_label)

        # # Fit model
        gd_pars = fit_model(model_label, model, train_data, train_paradigm, max_n_iterations=max_n_iterations)

        # pred = model.predict(parameters=gd_pars, paradigm=paradigm)
        # r2 = get_rsq(data, pred)
        # print(r2.describe())

        conditionwise_pars = get_conditionspecific_parameters(model_label, model, gd_pars)
        print(conditionwise_pars)

        model.set_paradigm(test_paradigm)
        test_pred = model.predict(paradigm=test_paradigm, parameters=gd_pars)

        cvr2 = get_rsq(test_data, test_pred)

        print(cvr2.describe())

        all_cvr2.append(cvr2)
    
    all_cvr2 = pd.concat(all_cvr2, axis=1)
    mean_cvr2 = all_cvr2.mean(axis=1)

    target_fn = op.join(target_dir, f'sub-{subject}_desc-cvr2.optim_space-T1w_pars.nii.gz')
    ips_masker.inverse_transform(mean_cvr2).to_filename(target_fn)

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
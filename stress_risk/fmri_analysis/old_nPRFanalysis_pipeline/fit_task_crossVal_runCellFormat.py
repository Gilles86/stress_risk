# leave one out cross validation
# from risk_experiment/risk_experiment/encoding_model/fit_task_cv.py

#%%
import braincoder
from braincoder.models import GaussianPRF
from braincoder.optimize import ParameterFitter
from braincoder.utils import get_rsq

import os.path as op
import pandas as pd
from nilearn import surface, image
from nilearn.input_data import NiftiMasker
import numpy as np

# in risk_experiment/risk_experiment/utils/data.py 
def get_target_dir(subject, session, sourcedata, base, modality='func'):
    target_dir = op.join(sourcedata, 'derivatives', base, f'sub-{subject}', f'ses-{session}',
                         modality)

    if not op.exists(target_dir):
        os.makedirs(target_dir)

    return target_dir
# %%
bids_folder = '/Users/mrenke/data/ds-stressrisk'
subject = '02'
session = 1

stimulus_range = np.linspace(np.log(5), np.log(80), 100)
space = 'fsnative'
smoothed=True  
pca_confounds=False
N_runs = 1 + 6 #the way python counts
task_name='risk'

# %%
key = 'glm_stim1'
target_dir = 'encoding_model.cv'

if smoothed:
    key += '.smoothed'
    target_dir += '.smoothed'

if pca_confounds:
    key += '.pca_confounds'
    target_dir += '.pca_confounds'

target_dir = get_target_dir(subject, session, bids_folder, target_dir)

paradigm = [pd.read_csv(op.join(bids_folder, f'sub-{subject}', f'ses-{session}',
                                'func', f'sub-{subject}_ses-{session}_task-{task_name}_run-{run}_events.tsv'), sep='\t')
            for run in range(1, N_runs)]
paradigm = pd.concat(paradigm, keys=range(1, N_runs), names=['run'])
paradigm = paradigm[paradigm.trial_type ==
                    'stimulus 1'].set_index('trial_nr', append=True)

paradigm['log(n1)'] = np.log(paradigm['n1'])
paradigm = paradigm['log(n1)']

#%%

model = GaussianPRF()
# SET UP GRID
mus = np.log(np.linspace(5, 80, 30, dtype=np.float32))
sds = np.log(np.linspace(2, 30, 30, dtype=np.float32))
amplitudes = np.array([1.], dtype=np.float32)
baselines = np.array([0], dtype=np.float32)

mask = op.join(bids_folder, 'derivatives',
                f'fmriprep/sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-{task_name}_run-1_space-T1w_desc-brain_mask.nii.gz')

masker = NiftiMasker(mask_img=mask)

data = op.join(bids_folder, 'derivatives', key,
                f'sub-{subject}', f'ses-{session}', 'func', f'sub-{subject}_ses-{session}_task-{task_name}_space-T1w_desc-stims1_pe.nii.gz')
# NiftiMasker.fit_transform: output [n_samples, n_features_new] = {n_trials, n_voxels}
data = pd.DataFrame(masker.fit_transform(data), index=paradigm.index)
print(data)

data = pd.DataFrame(data, index=paradigm.index)
#%%
for test_run in range(1, N_runs):

    test_data, test_paradigm = data.loc[test_run].copy(
    ), paradigm.loc[test_run].copy()
    print(test_data, test_paradigm)
    train_data, train_paradigm = data.drop(
        test_run, level='run').copy(), paradigm.drop(test_run, level='run').copy()

    optimizer = ParameterFitter(model, train_data, train_paradigm)

    grid_parameters = optimizer.fit_grid(
        mus, sds, amplitudes, baselines, use_correlation_cost=True)
    grid_parameters = optimizer.refine_baseline_and_amplitude(
        grid_parameters, n_iterations=2)

    optimizer.fit(init_pars=grid_parameters, learning_rate=.05, store_intermediate_parameters=False, max_n_iterations=10000,
                    r2_atol=0.00001)

    target_fn = op.join(
        target_dir, f'sub-{subject}_ses-{session}_run-{test_run}_desc-r2.optim_space-T1w_pars.nii.gz')
    # r2.nii file 
    masker.inverse_transform(optimizer.r2).to_filename(target_fn)
# function calculates residuals ((data - predictions)**2; sum) and puts into context with data-variance and then: r2 = (1 - (ssq_resid / ssq_data))
    cv_r2 = get_rsq(test_data, model.predict(parameters=optimizer.estimated_parameters,
                                                paradigm=test_paradigm.astype(np.float32)))

    target_fn = op.join(
        target_dir, f'sub-{subject}_ses-{session}_run-{test_run}_desc-cvr2.optim_space-T1w_pars.nii.gz')
    # cvr2.nii file 
    masker.inverse_transform(cv_r2).to_filename(target_fn)

    for par, values in optimizer.estimated_parameters.T.iterrows():
        print(values)
        target_fn = op.join(
            target_dir, f'sub-{subject}_ses-{session}_run-{test_run}_desc-{par}.optim_space-T1w_pars.nii.gz')

        masker.inverse_transform(values).to_filename(target_fn)
# %%

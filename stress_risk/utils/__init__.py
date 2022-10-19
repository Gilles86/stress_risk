from .data import Subject
#%%
import os.path as op
from nilearn.glm.first_level import make_first_level_design_matrix
from nilearn import surface, image
from nilearn.maskers import NiftiMasker
import nibabel as nb
import pandas as pd
import numpy as np
from nibabel import gifti
from tqdm import tqdm
from tqdm.contrib.itertools import product
from sklearn.decomposition import PCA

import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

#%%
def get_volume_mask(subject, session, mask, bids_folder='/data', task_name = 'risk'):

    # if session.endswith('1'):   task  = 'mapper'; else:  task  = 'task'

    base_mask = op.join(bids_folder, 'derivatives', f'fmriprep/sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-{task_name}_run-1_space-T1w_desc-brain_mask.nii.gz')

    if mask is None:
        return base_mask

    #mask = mask.replace('_', '')
    #mask = op.join(bids_folder, 'derivatives', 'ips_masks', f'sub-{subject}', f'sub-{subject}_space-T1w_desc-{mask}_mask.nii.gz')
    mask = op.join(bids_folder, 'derivatives', 'ips_masks', f'sub-{subject}',f'sub-{subject}_space-T1w_desc-{mask}.nii.gz')
    mask = image.resample_to_img(mask, base_mask, interpolation='nearest')

    return mask

#%%
def get_single_trial_volume(subject, session, mask=None, bids_folder='/data',
        smoothed=False,
        pca_confounds=False,
        task_name = 'risk'
        ):

    key= 'glm_stim1'

    if smoothed:
        key += '.smoothed'

    if pca_confounds:
        key += '.pca_confounds'

    fn = op.join(bids_folder, 'derivatives', key, f'sub-{subject}', f'ses-{session}', 'func', 
            f'sub-{subject}_ses-{session}_task-{task_name}_space-T1w_desc-stims1_pe.nii.gz')

    im = image.load_img(fn)
    
    mask = get_volume_mask(subject, session, mask, bids_folder, task_name)
    # paradigm = get_task_behavior(subject, session, bids_folder)
    masker = NiftiMasker(mask_img=mask)

    data = pd.DataFrame(masker.fit_transform(im))

    return data

#%%
def get_prf_parameters_volume(subject, session, bids_folder,
        run=None,
        smoothed=False,
        pca_confounds=False,
        cross_validated=True,
        hemi=None,
        mask=None,
        space='fsnative'):

    dir = 'encoding_model'
    if cross_validated:
        if run is None:
            raise Exception('Give run')

        dir += '.cv'

    if smoothed:
        dir += '.smoothed'

    if pca_confounds:
        dir += '.pca_confounds'

    parameters = []

    keys = ['mu', 'sd', 'amplitude', 'baseline']

    mask = get_volume_mask(subject, session, mask, bids_folder)
    masker = NiftiMasker(mask)

    for parameter_key in keys:
        if cross_validated:
            fn = op.join(bids_folder, 'derivatives', dir, f'sub-{subject}', f'ses-{session}', 
                    'func', f'sub-{subject}_ses-{session}_run-{run}_desc-{parameter_key}.optim_space-T1w_pars.nii.gz')
        else:
            fn = op.join(bids_folder, 'derivatives', dir, f'sub-{subject}', f'ses-{session}', 
                    'func', f'sub-{subject}_ses-{session}_desc-{parameter_key}.optim_space-T1w_pars.nii.gz')
        
        pars = pd.Series(masker.fit_transform(fn).ravel())
        parameters.append(pars)

    return pd.concat(parameters, axis=1, keys=keys, names=['parameter'])

#%%
def get_surf_mask(subject, mask, hemi=None, bids_folder='/data'):

    if hemi is None:
        mask_l = get_surf_mask(subject, mask, 'L', bids_folder )
        mask_r = get_surf_mask(subject, mask, 'R', bids_folder )
        return pd.concat((mask_l, mask_r), axis=1, keys=['L', 'R'], names=['hemi'])
        

    fs_hemi = {'L':'lh', 'R':'rh'}[hemi]

    fs_subject = f'sub-{subject}'
    fn = op.join(bids_folder, 'derivatives', 'freesurfer', 
            get_fs_subject(subject), 'surf',
            f'{fs_hemi}.{mask}.mgz')

    d = surface.load_surf_data(fn).astype(np.bool)
    d = pd.Series(d, index=pd.Index(np.arange(len(d)), name='vertex'))
    return d

#%%

# %%
def get_target_dir(subject, session, sourcedata, base, modality='func'):
    target_dir = op.join(sourcedata, 'derivatives', base, f'sub-{subject}', f'ses-{session}',
                         modality)

    if not op.exists(target_dir):
        os.makedirs(target_dir)

    return target_dir
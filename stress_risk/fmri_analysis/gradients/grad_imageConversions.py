# various steps for gradient analysis
# 1. mri_surf2surf : transform fsavergae to fsaverage5 (via nipype)
# 2. gradients_01.py 
# 3. mri_surf2surf : from fsaverage5 to fsnative

#%%
import numpy as np
import os.path as op
from nipype.interfaces.freesurfer import SurfaceTransform

sub = '09'
ses = 1
bids_folder = '/Users/mrenke/data/ds-stressrisk'

#%% 1. mri_surf2surf : transform fsavergae to fsaverage5 (via nipype)
runs = range(1,7)

for run in runs:
    for hemi in ['L', 'R']:
        sxfm = SurfaceTransform(subjects_dir='/Users/mrenke/data/ds-stressrisk/derivatives/freesurfer')
        in_file = f'sub-{sub}_ses-{ses}_task-risk_run-{run}_space-fsaverage_hemi-{hemi}_bold.func.gii'
        in_file_path = op.join(bids_folder, 'derivatives', 'fmriprep', f'sub-{sub}',f'ses-{ses}','func',in_file)
        out_file = f'sub-{sub}_ses-{ses}_task-risk_run-{run}_space-fsaverage5_hemi-{hemi}_bold.func.gii'
        out_file_path = op.join(bids_folder, 'derivatives', 'fmriprep', f'sub-{sub}',f'ses-{ses}','func',out_file)

        sxfm.inputs.source_file = in_file_path
        sxfm.inputs.out_file = out_file_path

        sxfm.inputs.source_subject = 'fsaverage'
        sxfm.inputs.target_subject = 'fsaverage5'

        if hemi == 'L':
            sxfm.inputs.hemi = 'lh'
        elif hemi == 'R':
            sxfm.inputs.hemi = 'rh'

        r = sxfm.run()


# %% 3. from fsaverage5 to fsnative
from nipype.interfaces.freesurfer import SurfaceTransform

target_space = 'fsnative'

for i, hemi in enumerate(['L', 'R']):   

    sxfm = SurfaceTransform(subjects_dir='/Users/mrenke/data/ds-stressrisk/derivatives/freesurfer')

    grad_sub_dir = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}')

    in_file = op.join(grad_sub_dir, f'sub-{sub}_ses-{ses}_task-risk_space-fsaverage5_hemi-{hemi}_grad1.surf.gii')
    out_file = op.join(grad_sub_dir, f'sub-{sub}_ses-{ses}_task-risk_space-{target_space}_hemi-{hemi}_grad1.surf.gii')

    sxfm.inputs.source_file = in_file
    sxfm.inputs.out_file = out_file

    sxfm.inputs.source_subject = 'fsaverage5'
    sxfm.inputs.target_subject = f'sub-{sub}'

    if hemi == 'L':
        sxfm.inputs.hemi = 'lh'
    elif hemi == 'R':
        sxfm.inputs.hemi = 'rh'

    r = sxfm.run()
#%% 3.2. for _noLabels_noXX, both gradients

from nipype.interfaces.freesurfer import SurfaceTransform
removedLabels = '_no120'

target_space = 'fsnative'

for n_grad in [1,2]:

    for i, hemi in enumerate(['L', 'R']):   

        sxfm = SurfaceTransform(subjects_dir='/Users/mrenke/data/ds-stressrisk/derivatives/freesurfer')

        grad_sub_dir = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}')

        in_file = op.join(grad_sub_dir, f'sub-{sub}_ses-{ses}_task-risk_space-fsaverage5_hemi-{hemi}_grad{n_grad}_noLabels{removedLabels}.surf.gii')
        out_file = op.join(grad_sub_dir, f'sub-{sub}_ses-{ses}_task-risk_space-{target_space}_hemi-{hemi}_grad{n_grad}_noLabels{removedLabels}.surf.gii')

        sxfm.inputs.source_file = in_file
        sxfm.inputs.out_file = out_file

        sxfm.inputs.source_subject = 'fsaverage5'
        sxfm.inputs.target_subject = f'sub-{sub}'

        if hemi == 'L':
            sxfm.inputs.hemi = 'lh'
        elif hemi == 'R':
            sxfm.inputs.hemi = 'rh'

        r = sxfm.run()


# %% if it does not run, running it in the terminal gives a better error message
# sxfm.cmdline --> paste into terminal
#%% save grad as fsaverage5.surf.gii
import nibabel as nib
import numpy as np
import os.path as op

bids_folder = '/Users/mrenke/data/ds-stressrisk'
sub = '03'
ses = 1
target_dir = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}')

grad1 =  np.load(op.join(target_dir, 'grad1_1.npy'))
grad1 = np.split(grad1,2) # for i, hemi in enumerate(['L', 'R']): --> left first?!

for i, hemi in enumerate(['L', 'R']):    

    gii_im_datar = nib.gifti.gifti.GiftiDataArray(data=grad1[i])
    gii_im = nib.gifti.gifti.GiftiImage(darrays= [gii_im_datar])

    target_dir = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}')

    if not op.exists(target_dir):
        os.makedirs(target_dir)

    out_file = op.join(target_dir, f'sub-{sub}_ses-{ses}_task-risk_space-fsaverage5_hemi-{hemi}_grad1.surf.gii')
    gii_im.to_filename(out_file) # https://nipy.org/nibabel/reference/nibabel.spatialimages.html


# %%

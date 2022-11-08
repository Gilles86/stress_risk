#%% only works with pycortec env (otehrwise deprication error from nibabel)
# create identy matrix necessary for surface visualization
from nilearn import image
import cortex
from cortex import freesurfer

import numpy as np
import os.path as op
import argparse

bids_folder = '/Users/mrenke/data/ds-stressrisk'
ses = 1

subject = 8
sub = '08'
base = 'encoding_model.smoothed'

def import_freesurfer_subject(subject, bids_folder):

    subject = int(subject)

    freesurfer.import_subj(f'sub-{subject:02d}', 
            freesurfer_subject_dir=op.join(bids_folder, 'derivatives', 'freesurfer'))

# %% create folder in pycortex-Database: ~mambaforge/share/pycortex/db/sub-
import_freesurfer_subject(subject, bids_folder)


# %%
par_file = op.join(bids_folder, 'derivatives', base , f'sub-{sub}', f'ses-{ses}', 'func', 
    f'sub-{sub}_ses-{ses}_desc-r2.optim_space-T1w_pars.nii.gz')

pars = image.load_img(par_file)

print(pars.shape)

transform = cortex.xfm.Transform(np.identity(4), pars)
transform.save(f'sub-{sub}', 'identity.bold')

# %%
 #ExpiredDeprecationError: get_affine method is deprecated. Please use the ``img.affine`` property instead.
 # --> changed ~/mambaforge/envs/numrefields_copy/lib/python3.10/site-packages/cortex/freesurfer.py:197, trans = nibabel.load(out).get_affine()[:3, -1]
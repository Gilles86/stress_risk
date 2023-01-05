
#%%
# environment: numrefields_copy OR pycortex
import cortex
from nilearn import image
import numpy as np
import os.path as op

sub = '05'

subject = f'sub-{sub}'
xfm = 'identity.bold'

bids_folder = '/Users/mrenke/data/ds-stressrisk'
ses = 1
base = 'encoding_model.smoothed'
#%%

r2_data =  op.join(bids_folder, 'derivatives', base , f'sub-{sub}', f'ses-{ses}', 'func', 
    f'sub-{sub}_ses-{ses}_desc-r2.optim_space-T1w_pars.nii.gz')
mu_data = op.join(bids_folder, 'derivatives', base , f'sub-{sub}', f'ses-{ses}', 'func', 
    f'sub-{sub}_ses-{ses}_desc-mu.optim_space-T1w_pars.nii.gz')


r2_data = image.load_img(r2_data).get_data().T
mu_data = image.load_img(mu_data).get_data().T

alpha = r2_data
alpha  = (alpha > .075).astype(np.float)

mu_data[r2_data < 0.05] = np.nan

r2_data_thr = r2_data.copy()
r2_data_thr[r2_data < 0.05] = np.nan

r2_surf = cortex.Volume(r2_data, subject, xfm)
r2_surf_thr = cortex.Volume(r2_data_thr, subject, xfm)
mu_surf = cortex.Volume(mu_data, subject, xfm)

ds = cortex.Dataset(r2=r2_surf,
                    r2_thr=r2_surf_thr,
                    mu=mu_surf)  # here change the IP to "localhost" for the webapplication to work!! e.g. http://localhost:47789/mixer.html
                

# make pycortex work:
# pip install git+https://github.com/gallantlab/pycortex.git
# sudo pip install numpy --upgrade --ignore-installed 

#%%


sub = '08'

subject = f'sub-{sub}'
xfm = 'identity.bold'

bids_folder = '/Users/mrenke/data/ds-stressrisk'
ses = 1
base = 'encoding_model.smoothed'


r2_data =  op.join(bids_folder, 'derivatives', base , f'sub-{sub}', f'ses-{ses}', 'func', 
    f'sub-{sub}_ses-{ses}_desc-r2.optim_space-T1w_pars.nii.gz')
mu_data = op.join(bids_folder, 'derivatives', base , f'sub-{sub}', f'ses-{ses}', 'func', 
    f'sub-{sub}_ses-{ses}_desc-mu.optim_space-T1w_pars.nii.gz')


r2_data = image.load_img(r2_data).get_data().T
mu_data = image.load_img(mu_data).get_data().T

alpha = r2_data
alpha  = (alpha > .075).astype(np.float)

mu_data[r2_data < 0.05] = np.nan

r2_data_thr = r2_data.copy()
r2_data_thr[r2_data < 0.05] = np.nan

r2_surf = cortex.Volume(r2_data, subject, xfm)
r2_surf_thr = cortex.Volume(r2_data_thr, subject, xfm)
mu_surf = cortex.Volume(mu_data, subject, xfm)

ds = cortex.Dataset(r2=r2_surf,
                    r2_thr=r2_surf_thr,
                    mu=mu_surf)

cortex.webshow(ds)                     

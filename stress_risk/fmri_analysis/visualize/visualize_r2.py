
#%%
import cortex
from nilearn import image
import numpy as np
#%%
subject = 'sub-01'
xfm = 'identity.bold'
#%%
r2_data = '/Users/mrenke/data/ds-tmspilot/derivatives/encoding_model.smoothed/sub-01/ses-2/func/sub-01_ses-2_desc-r2.optim_space-T1w_pars.nii.gz'
mu_data = '/Users/mrenke/data/ds-tmspilot/derivatives/encoding_model.smoothed/sub-01/ses-2/func/sub-01_ses-2_desc-mu.optim_space-T1w_pars.nii.gz'


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
                    r2_data_thr=r2_data_thr,
                    mu=mu_surf)

cortex.webshow(ds)                    
# here change the IP to "localhost" for the webapplication to work!!


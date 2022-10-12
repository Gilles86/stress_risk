#%%
# create identy matrix necessary for surface visualization
from nilearn import image
import cortex
import numpy as np

subject = '01'

par_file = '/Users/mrenke/data/ds-tmspilot/derivatives/encoding_model.smoothed/sub-01/ses-2/func/sub-01_ses-2_desc-r2.optim_space-T1w_pars.nii.gz'

pars = image.load_img(par_file)

print(pars.shape)

transform = cortex.xfm.Transform(np.identity(4), pars)
transform.save(f'sub-{subject}', 'identity.bold')
# %%

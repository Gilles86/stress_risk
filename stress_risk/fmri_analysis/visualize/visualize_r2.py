
#%%
# environment: numrefields_copy OR pycortex
import cortex
from nilearn import image
import numpy as np
import os.path as op

sub = '09'
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


#%%
import nibabel as nib
removedLabels = '_no120' # _no37-44 sub-01

ims = [[None]*2]*2
for grad_n_i, grad_n in enumerate([1,2]):
    for hemi_i, hemi in enumerate(['L', 'R']):  
        file = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}',
            f'sub-{sub}_ses-{ses}_task-risk_space-fsnative_hemi-{hemi}_grad{grad_n}_noLabels{removedLabels}.surf.gii')

        ims[grad_n_i][hemi_i] = nib.load(file)

grad1 = cortex.dataset.Vertex(np.concatenate([ims[0][0].agg_data(), ims[0][1].agg_data()], axis=0), subject=subject)
grad2 = cortex.dataset.Vertex(np.concatenate([ims[1][0].agg_data(), ims[1][1].agg_data()], axis=0), subject=subject)


#%%
ds = cortex.Dataset(r2=r2_surf,
                    r2_thr=r2_surf_thr,
                    mu=mu_surf, 
                    grad1 = grad1)
                    #grad2 = grad2) somehow does not work to display both in one webshow...."TypeError: byte indices must be integers or slices, not tuple"
                    
cortex.webshow(ds)    # here change the IP to "localhost" for the webapplication to work!! e.g. http://localhost:47789/mixer.html
                
# %%
grad_l = cortex.dataset.Vertex(ims[0].agg_data(), subject=subject)
grad_r = cortex.dataset.Vertex(ims[1].agg_data(), subject=subject)


#%%

#%%
ds = cortex.Dataset(r2=r2_surf,
                    r2_thr=r2_surf_thr,
                    mu=mu_surf, 
                    gradient1_L = grad_l,
                    gradient1_R = grad_r)


# make pycortex work:
# pip install git+https://github.com/gallantlab/pycortex.git
# sudo pip install numpy --upgrade --ignore-installed 

#%% save r2_surf to fsnative.surf.gii file

target_dir = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}')

dat = r2_surf.map().data

datL, datR = np.split(dat,[139846]) # look at grad1[0].agg_data().shape
#data = np.split(dat, 2); datL, datR = data[0], data[1]

# left 
gii_im_datar = nib.gifti.gifti.GiftiDataArray(data=datL)
gii_im = nib.gifti.gifti.GiftiImage(darrays= [gii_im_datar])
out_file = op.join(target_dir, f'sub-{sub}_ses-{ses}_task-risk_space-fsnative_hemi-L_r2.surf.gii')
gii_im.to_filename(out_file)
# right
gii_im_datar = nib.gifti.gifti.GiftiDataArray(data=datR)
gii_im = nib.gifti.gifti.GiftiImage(darrays= [gii_im_datar])
out_file = op.join(target_dir, f'sub-{sub}_ses-{ses}_task-risk_space-fsnative_hemi-R_r2.surf.gii')
gii_im.to_filename(out_file)
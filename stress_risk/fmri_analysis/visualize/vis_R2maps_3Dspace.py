# visualize R2 maps easily

#%%
import os.path  as op
import nilearn
import nibabel as nib
import numpy as np
import nilearn.plotting as nipl 

# %%
bids_folder = '/Users/mrenke/data/ds-stressrisk'
target_folder = op.join(bids_folder, 'plots_and ims', 'r2_in_nativeSpace')
ses = 1

sub_list_s = list(range(1,18))
sub_list= []
for e in sub_list_s:
    sub_list.append(str(e).zfill(2))

# %% loop to create images in 

for sub in sub_list:
    try: 
        anat_file = op.join(bids_folder, 'derivatives','fmriprep', f'sub-{sub}', 'ses-1', 'anat', f'sub-{sub}_ses-1_desc-preproc_T1w.nii.gz')
        r2_file = op.join(bids_folder, 'derivatives','encoding_model.smoothed', f'sub-{sub}', f'ses-{ses}', 'func', f'sub-{sub}_ses-{ses}_desc-r2.optim_space-T1w_pars.nii.gz')
        mask_file = op.join(bids_folder, 'derivatives','ips_masks', f'sub-{sub}', f'sub-{sub}_space-T1w_desc-NPC_R.nii.gz')
        
        anat_im = nib.load(anat_file)
        beta_im = nib.load(r2_file)
        mask_im = nib.load(mask_file)

        beta_im_dat = beta_im.get_data().squeeze() # (55, 68, 51)
        mask_im_dat = mask_im.get_data().squeeze() # (170, 256, 256)

        mask_in_epiSpace = niim.resample_to_img(mask_im, beta_im)
        mask_in_epiSpace_dat = mask_in_epiSpace.get_data().squeeze()# (55, 68, 51)

        # get indices of max betas within mask
        max_in_mask = np.where(beta_im_dat == np.max(beta_im_dat[ np.where(mask_in_epiSpace_dat > 0.5)]))
        max_in_mask_ = np.append(np.array(max_in_mask), [1])
        coords = np.dot(beta_im.affine, max_in_mask_)

        out_file = op.join(target_folder, f'sub-{sub}_ses-{ses}_R2map.png')
        nipl.plot_stat_map(beta_im, bg_img= anat_im, threshold = 0.13, cut_coords = (coords[0], coords[1], coords[2]), draw_cross=True, output_file=out_file) # (x: left-right, y: ant-post, z: vent-dorsal)
    except:
        print(sub)


# %%
#%%
ses = 1
sub = '01'


anat_file = op.join(bids_folder, 'derivatives','fmriprep', f'sub-{sub}', 'ses-1', 'anat', f'sub-{sub}_ses-1_desc-preproc_T1w.nii.gz')
r2_file = op.join(bids_folder, 'derivatives','encoding_model.smoothed', f'sub-{sub}', f'ses-{ses}', 'func', f'sub-{sub}_ses-{ses}_desc-r2.optim_space-T1w_pars.nii.gz')

mask_file = op.join(bids_folder, 'derivatives','ips_masks', f'sub-{sub}', f'sub-{sub}_space-T1w_desc-NPC_R.nii.gz')

out_file = op.join(bids_folder, 'plots_and ims', 'r2_in_nativeSpace', f'sub-{sub}_ses-{ses}_R2map.png')

#%%
import nilearn.plotting as nipl 

anat_im = nib.load(anat_file)
beta_im = nib.load(r2_file)
mask_im = nib.load(mask_file)


beta_im_dat = beta_im.get_data().squeeze() # (55, 68, 51)
mask_im_dat = mask_im.get_data().squeeze() # (170, 256, 256)
# %%
nipl.plot_stat_map(beta_im, bg_img= anat_im, threshold = 0.13) #, cut_coords = (-31, -66, 40), draw_cross=False)#, output_file=out_file) # (x: left-right, y: ant-post, z: vent-dorsal)

# %% interactive (slice wise)
#html_view = 
nipl.view_img(beta_im, bg_img= anat_im, threshold = 0.13)
nipl.view_img(mask_im, bg_img= anat_im, opacity = 0.8)

#html_view.open_in_browser()
# %%
import nilearn.image as niim
import numpy as np

mask_in_epiSpace = niim.resample_to_img(mask_im, beta_im)
mask_in_epiSpace_dat = mask_in_epiSpace.get_data().squeeze()# (55, 68, 51)

# get indices of max betas within mask
max_in_mask = np.where(beta_im_dat == np.max(beta_im_dat[ np.where(mask_in_epiSpace_dat > 0.5)]))
max_in_mask_ = np.append(np.array(max_in_mask), [1])
coords = np.dot(beta_im.affine, max_in_mask_)
# %%

nipl.plot_stat_map(beta_im, bg_img= anat_im, threshold = 0.13, cut_coords = (coords[0], coords[1], coords[2])) #, draw_cross=False)#, output_file=out_file) # (x: left-right, y: ant-post, z: vent-dorsal)


# np.where(mask_in_epiSpace_dat < 0.5)[1].shape == 189870
# np.where(mask_in_epiSpace_dat > 0.5)[1].shape ==870

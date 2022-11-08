# visualize R2 maps easily
# needs 3 files from bids_folder/derivatives/:
# -frmiprep/../anat/...ses-1_desc-preproc_T1w.nii.gz
# -encoding_model.smoothed/..../....desc-r2.optim_space-T1w_pars.nii.gz
# -ips_masks/../sub-{sub}_space-T1w_desc-NPC_R.nii.gz'

#%%
import os.path  as op
import matplotlib
from matplotlib import pyplot as plt
import nilearn
import nibabel as nib
import numpy as np
import nilearn.plotting as nipl 
import nilearn.image as niim
import matplotlib as mpl

# %%
bids_folder = '/Users/mrenke/data/ds-stressrisk'
denoise = True
smoothed = True

ses = 1

key = ''
target_dir = op.join(bids_folder, 'plots_and_ims', 'r2_in_nativeSpace')

if denoise:
    key += '.denoise'
    target_dir += '.denoise'
if smoothed:
    key += '.smoothed'
    target_dir += '.smoothed'

if not op.exists(target_dir):
    os.makedirs(target_dir)

target_folder = target_dir

sub_list_s = list(range(1,48+1))
sub_list= []
for e in sub_list_s:
    sub_list.append(str(e).zfill(2))

# %% loop to create images in 
#sub_list= [16,17,21,22]
for sub in sub_list:
    try: 
        anat_file = op.join(bids_folder, 'derivatives','fmriprep', f'sub-{sub}', 'ses-1', 'anat', f'sub-{sub}_ses-1_desc-preproc_T1w.nii.gz')
        r2_file = op.join(bids_folder, 'derivatives',f'encoding_model{key}', f'sub-{sub}', f'ses-{ses}', 'func', f'sub-{sub}_ses-{ses}_desc-r2.optim_space-T1w_pars.nii.gz')
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
        #nipl.plot_stat_map(beta_im, bg_img= anat_im, threshold = 0.13, cut_coords = (coords[0], coords[1], coords[2]), draw_cross=True, output_file= out_file) # (x: left-right, y: ant-post, z: vent-dorsal)

        display = nipl.plot_anat(anat_img = anat_im, cut_coords = (coords[0], coords[1], coords[2]))
        display.add_overlay(mask_im, cmap = mpl.colormaps['binary'], alpha = 0.5) # alpha = opacity/transparent
        display.add_overlay(beta_im, threshold = 0.13, colorbar=True, cmap = mpl.colormaps['hot'])
        nipl.show()
        display.savefig(out_file ,dpi=199)
    except:
        print(sub)


# %%

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
import matplotlib as mpl

display = nipl.plot_anat(anat_img = anat_im, cut_coords = (coords[0], coords[1], coords[2]))
display.add_overlay(mask_im, cmap = mpl.colormaps['binary'], alpha = 0.5)
display.add_overlay(beta_im, threshold = 0.13, colorbar=True, cmap = mpl.colormaps['hot'])
nipl.show()
display.savefig(out_file ,dpi=199)


#%%
spm = nipl.plot_stat_map(beta_im, bg_img= anat_im, threshold = 0.13, cut_coords = (coords[0], coords[1], coords[2]), draw_cross=True)
spm.add_overlay(mask_im, alhpa = 0.5)
nipl.show()

import matplotlib.pyplot as pl
fig_size_scaler = 2
#pl.figure(figsize =[fig_size_scaler*6.4, fig_size_scaler*4.8])
#%% put needed input files on local computer ()

# create folders for rsync of only anatomical scans (limited disk space)
import os
base = 'glm_stim1.denoise.smoothed'
dtype = 'func'
for sub in sub_list:
    try: 
        os.mkdir(op.join(bids_folder,'derivatives',base , f'sub-{sub}'))
        os.mkdir(op.join(bids_folder,'derivatives',base , f'sub-{sub}', 'ses-1'))
        os.mkdir(op.join(bids_folder,'derivatives',base, f'sub-{sub}', 'ses-1', dtype))
    except:
        print(sub)

# %% & then in terminal (VSC)
for subject in 22 23 24 25 26 27 28 29 30 31 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48; 
do rsync -rcvz 
sciencecluster:/data/mrenke/ds-stressrisk/derivatives/fmriprep/sub-${subject}/ses-1/anat/sub-${subject}_ses-1_desc-preproc_T1w.nii.gz
 ~/data/ds-stressrisk/derivatives/fmriprep/sub-${subject}/ses-1/anat;
done;

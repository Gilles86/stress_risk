# generate gradients from task
# needs in fmriprep folder:
#  - bold-data in fsaverage5 space --> grad_imConversion first
#  - confound-file: _desc-confounds_timeseries.tsv


#%%
import numpy as np
import nibabel as nib
import os.path as op

import pandas as pd
from nilearn import signal

from nilearn import datasets
from brainspace.utils.parcellation import reduce_by_labels

# %%
bids_folder = '/Users/mrenke/data/ds-stressrisk'

sub = '06' 
ses = 1
runs = range(1, 7)

space = 'fsaverage5' # 'fsnative'

#%% 1 & 2: load in data as timeseries and regress out confounds (for each run sepeprately)
number_of_vertex = 20484  # 'fsaverage5', 10242 * 2

fmriprep_confounds_include = ['global_signal', 'dvars', 'framewise_displacement', 'trans_x',
                                  'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z',
                                  'a_comp_cor_00', 'a_comp_cor_01', 'a_comp_cor_02', 'a_comp_cor_03', 'cosine00', 'cosine01', 'cosine02'
                                  ] # 


clean_ts_runs = np.empty([number_of_vertex,0])

for run in runs:
    timeseries = [None] * 2
    for i, hemi in enumerate(['L', 'R']):
        filename = op.join(bids_folder,'derivatives', 'fmriprep', f'sub-{sub}', f'ses-{ses}', 'func', 
        f'sub-{sub}_ses-{ses}_task-risk_run-{run}_space-{space}_hemi-{hemi}_bold.func.gii')
        timeseries[i] = nib.load(filename).agg_data()
    timeseries = np.vstack(timeseries) # (20484, 135)

    fmriprep_confounds_file = op.join(bids_folder,'derivatives', 'fmriprep', f'sub-{sub}', f'ses-{ses}', 'func', f'sub-{sub}_ses-{ses}_task-risk_run-{run}_desc-confounds_timeseries.tsv')
    fmriprep_confounds = pd.read_table(fmriprep_confounds_file)[fmriprep_confounds_include] 
    fmriprep_confounds= fmriprep_confounds.fillna(method='bfill')

    #clean_ts_list[run] = signal.clean(timeseries.T, confounds=fmriprep_confounds).T
    clean_ts = signal.clean(timeseries.T, confounds=fmriprep_confounds).T

    clean_ts_runs = np.append(clean_ts_runs, clean_ts, axis=1)

clean_ts = clean_ts_runs

#%% 3. extract the cleaned timeseries onto a set of labels-------------------------------------------------------

atlas = datasets.fetch_atlas_surf_destrieux()

# Remove non-cortex regions
regions = atlas['labels'].copy()
masked_regions = [b'Medial_wall', b'Unknown']
masked_labels = [regions.index(r) for r in masked_regions]
for r in masked_regions:
    regions.remove(r)

# Build Destrieux parcellation and mask
labeling = np.concatenate([atlas['map_left'], atlas['map_right']])
mask = ~np.isin(labeling, masked_labels)

# Distinct labels for left and right hemispheres
lab_lh = atlas['map_left']
labeling[lab_lh.size:] += lab_lh.max() + 1 # regions left= 1-75; regions right = 76 - 151

# extract mean timeseries for each label
seed_ts = reduce_by_labels(clean_ts[mask], labeling[mask], axis=1, red_op='mean')


# %% 4. & 5.  ------------------------------------------------------------------------------
from nilearn.connectome import ConnectivityMeasure

correlation_measure = ConnectivityMeasure(kind='correlation')
correlation_matrix = correlation_measure.fit_transform([seed_ts.T])[0]

from nilearn import plotting

mat_mask = np.where(np.std(correlation_matrix, axis=1) > 0.2)[0] # # Reduce matrix size, only for visualization purposes

c = correlation_matrix[mat_mask][:, mat_mask]

# Create corresponding region names
regions_list = ['%s_%s' % (h, r.decode()) for h in ['L', 'R'] for r in regions]
masked_regions = [regions_list[i] for i in mat_mask]


corr_plot = plotting.plot_matrix(c, figure=(15, 15), labels=masked_regions,
                                 vmax=0.8, vmin=-0.8, reorder=True)


# %% 5. Run gradient analysis

from brainspace.gradient import GradientMaps

gm = GradientMaps(n_components=2, random_state=0) # Default is 'dm' = DiffusionMaps
gm.fit(correlation_matrix)

from brainspace.datasets import load_fsa5
from brainspace.plotting import plot_hemispheres
from brainspace.utils.parcellation import map_to_labels

# Map gradients to original parcels
grad = [None] * 2
for i, g in enumerate(gm.gradients_.T):
    grad[i] = map_to_labels(g, labeling, mask=mask, fill=np.nan)

target_dir = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}')

if not op.exists(target_dir):
    os.makedirs(target_dir)

np.save(op.join(target_dir,'grad1.npy'), grad[0])
np.save(op.join(target_dir,'grad2.npy'), grad[1])

#%% 6. save as fsaverage_hemi-{l/R}.surf.gii

for n_grad in [1,2]:
    grad = np.load(op.join(target_dir, f'grad{n_grad}.npy'))
    grad = np.split(grad,2) # for i, hemi in enumerate(['L', 'R']): --> left first?!

    for i, hemi in enumerate(['L', 'R']):    

        gii_im_datar = nib.gifti.gifti.GiftiDataArray(data=grad[i])
        gii_im = nib.gifti.gifti.GiftiImage(darrays= [gii_im_datar])

        out_file = op.join(target_dir, f'sub-{sub}_ses-{ses}_task-risk_space-fsaverage5_hemi-{hemi}_grad{n_grad}.surf.gii')
        gii_im.to_filename(out_file) # https://nipy.org/nibabel/reference/nibabel.spatialimages.html


#%% plot gradients
surf_lh, surf_rh = load_fsa5()

# sphinx_gallery_thumbnail_number = 2
plot_hemispheres(surf_lh, surf_rh, array_name=grad, size=(1200, 400), cmap='viridis_r',
                 color_bar=True, label_text=['Grad1', 'Grad2'], zoom=1.5)




#%% ---------------------------------------------------------------------
# run without parcellation----------------------------------------------------
from nilearn.connectome import ConnectivityMeasure
from brainspace.gradient import GradientMaps
from brainspace.utils.parcellation import map_to_labels

# grad1 range was weird: plt.hist(grad_noParcel[0]) --> solution: remove regions with weird eigenvector value

mask = ~np.isin(labeling, masked_labels)
mask[labeling == 103] = False # labeling[ grad_noParcel[0] == max(grad_noParcel[0])],37 sub-01; 113 sub-04 ?
mask[labeling == 69] = False # labeling[grad_noParcel[0] == min(grad_noParcel[0]) ], 44 sub-01; sub-09 120 (R, = b'S_central',on L: 44 (+ 76 )); 
mask[labeling == 118] = False 

seed_ts_noParcel = clean_ts[mask]

correlation_measure_noParcel = ConnectivityMeasure(kind='correlation')
correlation_matrix_noParcel = correlation_measure_noParcel.fit_transform([seed_ts_noParcel.T])[0]

gm_noParcel = GradientMaps(n_components=2, random_state=0)
gm_noParcel.fit(correlation_matrix_noParcel)

# Map gradients to original parcels
labeling_noParcel = np.arange(0,len(labeling),1,dtype = int)

grad_noParcel = [None] * 2
for i, g in enumerate(gm_noParcel.gradients_.T):
    grad_noParcel[i] = map_to_labels(g, labeling_noParcel, mask=mask, fill=np.nan)

    
#%% plot
from brainspace.datasets import load_fsa5
from brainspace.plotting import plot_hemispheres

surf_lh, surf_rh = load_fsa5()

plot_hemispheres(surf_lh, surf_rh, array_name=grad_noParcel, size=(1200, 400), cmap='viridis_r',
                 color_bar=True, label_text=['Grad1', 'Grad2'], zoom=1.5)



# %% save 
import os

removedLabels = '_no37-44' # sub-01
removedLabels = '_no120' #sub-09
removedLabels = '_no113-120' # sub-04
removedLabels = ''

grad = grad_noParcel

target_dir = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}')

if not op.exists(target_dir):
    os.makedirs(target_dir)

for i, n_grad  in enumerate([1,2]):
    np.save(op.join(target_dir,f'grad{n_grad}_noLabels{removedLabels}.npy'), grad[i])

for n_grad in [1,2]:
    grad = np.load(op.join(target_dir, f'grad{n_grad}_noLabels{removedLabels}.npy'))
    grad = np.split(grad,2) # for i, hemi in enumerate(['L', 'R']): --> left first?!

    for s, hemi in enumerate(['L', 'R']):    

        gii_im_datar = nib.gifti.gifti.GiftiDataArray(data=grad[i])
        gii_im = nib.gifti.gifti.GiftiImage(darrays= [gii_im_datar])

        out_file = op.join(target_dir, f'sub-{sub}_ses-{ses}_task-risk_space-fsaverage5_hemi-{hemi}_grad{n_grad}_noLabels{removedLabels}.surf.gii')
        gii_im.to_filename(out_file) # https://nipy.org/nibabel/reference/nibabel.spatialimages.html


# %%

##----------old---------------- way to load data in and regress condfounds out
# %% 1. load in data as timeseries
number_of_vertex = 274092  # 'fsnative'
number_of_vertex = 327684   # 'fsaverage'
number_of_vertex = 20484  # 'fsaverage5'

timeseries_run_concat = np.empty([number_of_vertex,0])
for run in runs:
    timeseries = [None] * 2
    for i, hemi in enumerate(['L', 'R']):
        filename = op.join(bids_folder,'derivatives', 'fmriprep', f'sub-{sub}', f'ses-{ses}', 'func', 
        f'sub-{sub}_ses-{ses}_task-risk_run-{run}_space-{space}_hemi-{hemi}_bold.func.gii')
        timeseries[i] = nib.load(filename).agg_data()
    timeseries = np.vstack(timeseries) # (274092, 135)
    timeseries_run_concat = np.append(timeseries_run_concat, timeseries, axis=1)
timeseries = timeseries_run_concat 
# %%
fmriprep_confounds_include = ['global_signal', 'dvars', 'framewise_displacement', 'trans_x',
                                  'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z',
                                  'a_comp_cor_00', 'a_comp_cor_01', 'a_comp_cor_02', 'a_comp_cor_03', 'cosine00', 'cosine01', 'cosine02'
                                  ]
fmriprep_confounds_run_concat = np.empty([0, len(fmriprep_confounds_include),])
for run in runs:
    fmriprep_confounds_file = op.join(bids_folder,'derivatives', 'fmriprep', f'sub-{sub}', f'ses-{ses}', 'func', f'sub-{sub}_ses-{ses}_task-risk_run-{run}_desc-confounds_timeseries.tsv')
    fmriprep_confounds = pd.read_table(fmriprep_confounds_file)[fmriprep_confounds_include] 
    fmriprep_confounds= fmriprep_confounds.fillna(method='bfill')
    fmriprep_confounds_run_concat = np.append(fmriprep_confounds_run_concat, fmriprep_confounds, axis=0)

fmriprep_confounds = fmriprep_confounds_run_concat

clean_ts = signal.clean(timeseries.T, confounds=fmriprep_confounds).T

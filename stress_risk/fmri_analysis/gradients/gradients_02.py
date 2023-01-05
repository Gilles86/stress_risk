#%%
import matplotlib.pyplot as plt
from nilearn.connectome import ConnectivityMeasure
from brainspace.gradient import GradientMaps
from brainspace.utils.parcellation import map_to_labels
import numpy as np
import nibabel as nib
from nilearn import datasets
import os.path as op
import os
from nilearn import signal
import pandas as pd
from scipy.sparse.csgraph import connected_components

bids_folder = '/Users/mrenke/data/ds-stressrisk'

subList = ['01','02','03','04','05','08','09']
subList = ['10','11','12','13']
subList = ['14','16','17','18','19']
ses = 1

#%%

atlas = datasets.fetch_atlas_surf_destrieux()
regions = atlas['labels'].copy()
masked_regions = [b'Medial_wall', b'Unknown']
masked_labels = [regions.index(r) for r in masked_regions]
for r in masked_regions:
    regions.remove(r)

# Build Destrieux parcellation and mask
labeling = np.concatenate([atlas['map_left'], atlas['map_right']])
labeling_noParcel = np.arange(0,len(labeling),1,dtype = int)     # Map gradients to original parcels


for sub in subList:

    mask = ~np.isin(labeling, masked_labels)
    mask[mask == False] =  True
    clean_ts = cleanTS(sub, ses)
    seed_ts_noParcel = clean_ts[mask]

    # filter out nodes that are not connected to the rest
    correlation_measure_noParcel = ConnectivityMeasure(kind='correlation')
    graph = correlation_measure_noParcel.fit_transform([seed_ts_noParcel.T])[0] #correlation_matrix_noParcel
    cc = connected_components(graph)
    mask_cc = cc[1] == 0 # all nodes in 0 belong to the largest connected component, check #-components in cc[0]
    mask[mask == True] = mask_cc # mark nodes not in component 0  as False in mask

    seed_ts_noParcel = clean_ts[mask]

    #now perform embedding on cleaned data
    correlation_measure_noParcel = ConnectivityMeasure(kind='correlation')
    correlation_matrix_noParcel = correlation_measure_noParcel.fit_transform([seed_ts_noParcel.T])[0]
    gm_noParcel = GradientMaps(n_components=2, random_state=0)
    gm_noParcel.fit(correlation_matrix_noParcel)

    grad_noParcel = [None] * 2
    for i, g in enumerate(gm_noParcel.gradients_.T):
        grad_noParcel[i] = map_to_labels(g, labeling_noParcel, mask=mask, fill=np.nan)

    saveGradToFiles(grad_noParcel, sub,ses,specification='')
    fs5Tofsnative(sub,ses)

#%%
def cleanTS(sub, ses, runs = range(1, 7),space = 'fsaverage5'):
    # load in data as timeseries and regress out confounds (for each run sepeprately)
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

    return clean_ts_runs

#%% 

def saveGradToFiles(grad, sub,ses, specification=''):
    target_dir = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}')

    if not op.exists(target_dir):
        os.makedirs(target_dir)

    for i, n_grad  in enumerate([1,2]):
        np.save(op.join(target_dir,f'grad{n_grad}_noParcel{specification}.npy'), grad[i])

    for n_grad in [1,2]:
        grad = np.load(op.join(target_dir, f'grad{n_grad}_noParcel{specification}.npy'))
        grad = np.split(grad,2) # for i, hemi in enumerate(['L', 'R']): --> left first

        for s, hemi in enumerate(['L', 'R']):    

            gii_im_datar = nib.gifti.gifti.GiftiDataArray(data=grad[i])
            gii_im = nib.gifti.gifti.GiftiImage(darrays= [gii_im_datar])

            out_file = op.join(target_dir, f'sub-{sub}_ses-{ses}_task-risk_space-fsaverage5_hemi-{hemi}_grad{n_grad}_noParcel{specification}.surf.gii')
            gii_im.to_filename(out_file) # https://nipy.org/nibabel/reference/nibabel.spatialimages.html

#%%
from nipype.interfaces.freesurfer import SurfaceTransform

def fs5Tofsnative(sub,ses, bids_folder='/Users/mrenke/data/ds-stressrisk'):

    target_space = 'fsnative'

    for n_grad in [1,2]:

        for i, hemi in enumerate(['L', 'R']):   

            sxfm = SurfaceTransform(subjects_dir='/Users/mrenke/data/ds-stressrisk/derivatives/freesurfer')

            grad_sub_dir = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}')

            in_file = op.join(grad_sub_dir, f'sub-{sub}_ses-{ses}_task-risk_space-fsaverage5_hemi-{hemi}_grad{n_grad}_noParcel.surf.gii')
            out_file = op.join(grad_sub_dir, f'sub-{sub}_ses-{ses}_task-risk_space-{target_space}_hemi-{hemi}_grad{n_grad}_noParcel.surf.gii')

            sxfm.inputs.source_file = in_file
            sxfm.inputs.out_file = out_file

            sxfm.inputs.source_subject = 'fsaverage5'
            sxfm.inputs.target_subject = f'sub-{sub}'

            if hemi == 'L':
                sxfm.inputs.hemi = 'lh'
            elif hemi == 'R':
                sxfm.inputs.hemi = 'rh'

            r = sxfm.run()

# %%

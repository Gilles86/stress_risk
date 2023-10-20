#%% Loop for gradient estimation and 
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
from utils import fsavTofsav5,cleanTS, saveGradToNPFile, npFileTofs5Gii,fsav5Tofsnative

bids_folder = '/Users/mrenke/data/ds-stressrisk'
bids_folder = '/Volumes/mrenkeED/data/ds-stressrisk'

subList = ['01','02','03','04','05','08','09','10','11','12','13','14']
subList = ['14','16','17','18','19']
subList = ['21']
ses = 1
specification=''
#specification='_dmask'

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

    fsavTofsav5(sub,ses, bids_folder=bids_folder)

    mask = ~np.isin(labeling, masked_labels) # generate a new, raw mask for each sub, that can be worked on later
    #mask[mask == False] =  True # remove "brainspace's default regions excluded"
    clean_ts = cleanTS(sub, ses,bids_folder=bids_folder)
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

    saveGradToNPFile(grad_noParcel, sub,ses, specification,bids_folder=bids_folder)
    npFileTofs5Gii(sub,ses, specification,bids_folder=bids_folder)
    fsav5Tofsnative(sub,ses,specification,bids_folder=bids_folder)
# %%

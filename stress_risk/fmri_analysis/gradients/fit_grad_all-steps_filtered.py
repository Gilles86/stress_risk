# all steps of the gradient generation process combined,
# hence: needs freesurfer directory for 1. fsavTofsav5 (laoding in), then fsav5Tofsnative (save)
# 

import argparse
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

def main(sub,ses,bids_folder,specification):

    # Build Destrieux parcellation and mask
    atlas = datasets.fetch_atlas_surf_destrieux()
    regions = atlas['labels'].copy()
    masked_regions = [b'Medial_wall', b'Unknown']
    masked_labels = [regions.index(r) for r in masked_regions]
    for r in masked_regions:
        regions.remove(r)
    labeling = np.concatenate([atlas['map_left'], atlas['map_right']])
    labeling_noParcel = np.arange(0,len(labeling),1,dtype = int)     # Map gradients to original parcels
    mask = ~np.isin(labeling, masked_labels) # generate a new, raw mask for each sub, that can be worked on later

    # subject
    #fsavTofsav5(sub,ses, bids_folder=bids_folder) 
    clean_ts = cleanTS(sub, ses,bids_folder=bids_folder)
    seed_ts_noParcel = clean_ts[mask]
    correlation_measure_noParcel = ConnectivityMeasure(kind='correlation')
    print('raw connectivity matrix estimated')

    # filter out nodes that are not connected to the rest
    graph = correlation_measure_noParcel.fit_transform([seed_ts_noParcel.T])[0] #correlation_matrix_noParcel
    cc = connected_components(graph)
    mask_cc = cc[1] == 0 # all nodes in 0 belong to the largest connected component, check #-components in cc[0]
    mask[mask == True] = mask_cc # mark nodes not in component 0  as False in mask
    print('mask with connected components created')

    seed_ts_noParcel = clean_ts[mask]

    #now perform embedding on cleaned data
    correlation_measure_noParcel = ConnectivityMeasure(kind='correlation')
    correlation_matrix_noParcel = correlation_measure_noParcel.fit_transform([seed_ts_noParcel.T])[0]
    gm_noParcel = GradientMaps(n_components=2, random_state=0)
    gm_noParcel.fit(correlation_matrix_noParcel)

    grad_noParcel = [None] * 2
    for i, g in enumerate(gm_noParcel.gradients_.T):
        grad_noParcel[i] = map_to_labels(g, labeling_noParcel, mask=mask, fill=np.nan)
    
    print('gradients generated')

    saveGradToNPFile(grad_noParcel, sub,ses, specification,bids_folder=bids_folder)
    npFileTofs5Gii(sub,ses, specification,bids_folder=bids_folder)
    fsav5Tofsnative(sub,ses,specification,bids_folder=bids_folder)   


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('subject', default=None)
    parser.add_argument('session', default=1, type=int)  
    parser.add_argument('--bids_folder', default='/Users/mrenke/data/ds-stressrisk')
    parser.add_argument('--specification', default='')
    cmd_args = parser.parse_args()

    main(cmd_args.subject, cmd_args.session, cmd_args.bids_folder, cmd_args.specification)
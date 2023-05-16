import argparse
from nilearn.connectome import ConnectivityMeasure
import numpy as np
from nilearn import datasets
import os.path as op
from utils import cleanTS
from scipy.sparse.csgraph import connected_components
import time

def main(sub,ses,bids_folder):
    s_time = time.time()

    atlas = datasets.fetch_atlas_surf_destrieux()
    regions = atlas['labels'].copy()
    masked_regions = [b'Medial_wall', b'Unknown']
    masked_labels = [regions.index(r) for r in masked_regions] # [42, 0]

    # Build Destrieux parcellation and mask
    labeling = np.concatenate([atlas['map_left'], atlas['map_right']]) # atlas['map_left'] == atlas.map_left -> array, each vertex has a label assignment (a number from 0-51)
    mask = ~np.isin(labeling, masked_labels) # False for masked_regions
    mask_a_cc = mask.copy() # for later

    clean_ts = cleanTS(sub, ses,bids_folder=bids_folder)
    seed_ts = clean_ts[mask] 

    correlation_measure = ConnectivityMeasure(kind='correlation')
    graph = correlation_measure.fit_transform([seed_ts.T])[0] #correlation_matrix_noParcel
    print(f'sub-{sub}: first correlation matrix estimated, after {np.round(time.time() - s_time)} seconds')
    target_folder = op.join(bids_folder,'derivatives','correlation_matrices')
    
    np.save(op.join(target_folder,f'sub-{sub}_ses-{ses}_corrMatrix_fsav5_unfiltered.npy'),graph)

  
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('subject', default=None)
    parser.add_argument('session', default=1, type=int)  
    parser.add_argument('--bids_folder', default='/data/ds-stressrisk')
    #parser.add_argument('--specification', default='')
    cmd_args = parser.parse_args()

    main(cmd_args.subject, cmd_args.session, cmd_args.bids_folder)
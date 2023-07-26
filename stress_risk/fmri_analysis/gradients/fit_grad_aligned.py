
from brainspace.gradient import GradientMaps
import os.path as op
import os
import numpy as np
import sys
import argparse
from time import process_time

t = process_time()

def main(sub,ses,bids_folder):

    t = process_time()
    source_folder = op.join(bids_folder,'derivatives','correlation_matrices')
    target_folder = op.join(bids_folder,'derivatives','gradients')

    cm_file = op.join(source_folder,f'sub-{sub}_ses-{ses}_corrMatrix_fsav5_unfiltered.npy')
    if op.isfile(cm_file):
        cm = np.load(cm_file)
    else:
        print('correlation matrix as to be generated first!!') 
        sys.exit()

    g_ref = np.load(op.join(bids_folder,'derivatives', 'gradients','gm_av50_unfiltered.npy')) # same labeling_noParcel as cm_unfiltered

    g_align = GradientMaps(kernel='normalized_angle', n_components=3,approach='le', alignment='procrustes')
    elapsed_time = process_time() - t
    print(f'{elapsed_time}: starting fitting')
    g_align.fit(cm,reference=g_ref)
    elapsed_time = process_time() - t
    print(f'{elapsed_time}: finished fitting')
    
    np.save(op.join(target_folder,f'sub-{sub}_ses-{ses}_ref-p-align_fsav5_unfiltered.npy'),g_align.gradients_) # 


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('subject', default=None)
    parser.add_argument('session', default=1, type=int)  
    parser.add_argument('--bids_folder', default='/data/ds-stressrisk')
    #parser.add_argument('--specification', default='')
    cmd_args = parser.parse_args()

    main(cmd_args.subject, cmd_args.session, cmd_args.bids_folder)
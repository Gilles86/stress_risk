
from brainspace.gradient import GradientMaps
import os.path as op
import os
import numpy as np
import sys
import argparse
from time import process_time

t = process_time()

def main(sub,ses,bids_folder,kernel,approach,ref_marg_align=False):

    t = process_time()
    source_folder = op.join(bids_folder,'derivatives','correlation_matrices')
    target_folder = op.join(bids_folder,'derivatives','gradients')

    cm_file = op.join(source_folder,f'sub-{sub}_ses-{ses}_corrMatrix_fsav5_unfiltered.npy')
    if op.isfile(cm_file):
        cm = np.load(cm_file)
    else:
        print(cm_file)
        print('correlation matrix as to be generated first!!') 
        sys.exit()

    if ref_marg_align:
        ref_specification = '_aligned-marg' 
    else:
        ref_specification = ''

    g_ref = np.load(op.join(bids_folder,'derivatives', 'gradients',f'gm_av50_unfiltered{ref_specification}.npy')) # same labeling_noParcel as cm_unfiltered

    g_align = GradientMaps(kernel=kernel, n_components=3,approach=approach, alignment='procrustes')
    elapsed_time = process_time() - t
    print(f'{elapsed_time}: starting fitting')
    g_align.fit(cm,reference=g_ref)
    elapsed_time = process_time() - t
    print(f'{elapsed_time}: finished fitting')
    
    kernel_specification = f'_kernel-{kernel}'

    np.save(op.join(target_folder,f'sub-{sub}_ses-{ses}_ref-p-align_fsav5_unfiltered{kernel_specification}{ref_specification}.npy'),g_align.gradients_) # 


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('subject', default=None)
    parser.add_argument('session', default=1, type=int)  
    parser.add_argument('--bids_folder', default='/data/ds-stressrisk')
    parser.add_argument('--kernel', default=None) # 'normalized_angle',  #Kernel function. If None, only sparsify. Default is None.
    parser.add_argument('--approach', default='dm')# Embedding approach. Default is 'dm'
    parser.add_argument('--ref_marg_align', action='store_true')

    #parser.add_argument('--specification', default='')
    cmd_args = parser.parse_args()

    main(cmd_args.subject, cmd_args.session, cmd_args.bids_folder, 
          cmd_args.kernel, cmd_args.approach,
          cmd_args.ref_marg_align,)
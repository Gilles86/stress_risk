import argparse
import cortex
import os.path as op
from cortex import webgl 
from nilearn import image
from nilearn import surface

import numpy as np
from utils import get_alpha_vertex
import pandas as pd

from stress_risk.utils.data import Subject

# run via:  %run visualize_nPRFmodel_subject.py 59 

def main(mask_by_ips=True, threshold=None, filter_extreme_prfs=True, vmax=28.0):

    subject = 59
    use_cvr2=False # 


    subject = int(subject)
    print(use_cvr2, threshold)

    #sub = Subject(subject, bids_folder = bids_folder)

    space = 'fsnative'
    fs_subject =  f'stressrisk.sub-{subject:02d}' # that is how the corresponding freesurfer registration is stored in pycortex

    vertices = {}

    if threshold is None:
        threshold = 0.05
    
    # GET PRF PARAMETERS
    pati = '/Users/mrenke/data/ds-stressrisk/derivatives/nifiti_toVisualize/sub-59/ses-1/func/'
    parameter_keys = ['mu', 'sd',  'r2']

    prf_pars = []
    for hemi in ['L', 'R']:
        parameters = []
        for parameter_key in parameter_keys:
            fn = op.join(pati, f'sub-59_ses-1_desc-{parameter_key}.optim.nilearn_space-fsnative_hemi-{hemi}.func.gii')
            pars = pd.Series(surface.load_surf_data(fn))
            pars.index.name = 'vertex'
            parameters.append(pars)

        prf_pars_hemi =  pd.concat(parameters, axis=1, keys=parameter_keys, names=['parameter'])
        prf_pars.append(prf_pars_hemi)

    prf_pars = pd.concat(prf_pars, axis=0, keys=['L', 'R'], names=['hemi'])
    print(prf_pars.head())
    print(len(prf_pars))
    prf_pars['mu'] = np.exp(prf_pars['mu'])

    mask = (prf_pars['r2']  > threshold).values

    if filter_extreme_prfs:
        print("Filtering extreme prfs")
        mask = mask & (prf_pars['mu'] > 5).values & (prf_pars['mu'] < 28).values

    if mask_by_ips:
        ips_L =  '/Users/mrenke/data/ds-stressrisk/derivatives/ips_masks/sub-59/sub-59_desc-NPC_L_space-fsnative_hemi-lh.ips.gii'
        ips_R =  '/Users/mrenke/data/ds-stressrisk/derivatives/ips_masks/sub-59/sub-59_desc-NPC_R_space-fsnative_hemi-rh.ips.gii'
        ips_mask = np.concatenate([surface.load_surf_data(ips_L), surface.load_surf_data(ips_R)])
        ips_mask = ips_mask.astype(np.bool)
        mask = mask & ips_mask

    print('check')
    mu_vertex = get_alpha_vertex(prf_pars['mu'].values, mask, vmin=5, vmax=vmax, subject=fs_subject) 
    r2_vertex = get_alpha_vertex(prf_pars['r2'].values, mask, cmap='hot', vmin=threshold, vmax=0.25, subject=fs_subject)
    #cvr2_vertex = get_alpha_vertex(prf_pars['cvr2'].values, mask, cmap='hot', vmin=0.0, vmax=0.25, subject=fs_subject)

    vertices[f"sub-{subject}_mu_vertex"] = mu_vertex
    vertices[f"sub-{subject}_r2_vertex"] = r2_vertex
    #vertices[f"cvr2_vertex_session_{session}"] = cvr2_vertex

    vertices = {k: v for k, v in sorted(vertices.items(), key=lambda item: item[0])}
    webgl.show(vertices)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--threshold', default=None, type=float)
    parser.add_argument('--no_mu_filter', dest='filter_extreme_prfs', action='store_false')
    parser.add_argument('--vmax', default=28, type=float)

    args = parser.parse_args()
    main(threshold=args.threshold, filter_extreme_prfs=args.filter_extreme_prfs, vmax=args.vmax) 
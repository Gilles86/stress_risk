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

# run via:  %run visualize_nPRFmodel_subject.py 59 --fsnative --key encoding_model.denoise.retroicor.smoothed

def main(subject, bids_folder, key,both_sessions = True,
         mask_by_ips=True, use_cvr2=False, threshold=None, filter_extreme_prfs=True, smoothed=False, fsnative=False,
         vmax=28.0):

    use_cvr2=False # 
    both_sessions = True

    subject = int(subject)
    print(use_cvr2, threshold)

    sub = Subject(subject, bids_folder = bids_folder)

    if fsnative:
        space = 'fsnative'
    else:
        space = 'fsaverage'

    if not fsnative :
        fs_subject = 'fsaverage' 
    elif fsnative:
        if bids_folder == '/Volumes/mrenkeED/data/ds-stressrisk':
            fs_subject =  f'stressrisk.sub-{subject:02d}' # that is how the corresponding freesurfer registration is stored in pycortex
        elif bids_folder == '/Users/mrenke/data/ds-stressrisk':
            fs_subject =  f'sub-{subject:02d}'

    vertices = {}

    if use_cvr2 and (threshold is None):
        threshold = 0.0
    elif not use_cvr2 and (threshold is None):
        threshold = 0.05
    
    sessions = [1,2] if both_sessions else [1]
    print(sessions)

    for session in sessions:
        prf_pars = sub.get_prf_parameters_surf(session, run=None,  key=key, nilearn=True, space=space)
        print(prf_pars.head())
        print(len(prf_pars))
        prf_pars['mu'] = np.exp(prf_pars['mu'])
        if use_cvr2:
            mask = (prf_pars['cvr2']  > threshold).values
        else:
            mask = (prf_pars['r2']  > threshold).values

        if filter_extreme_prfs:
            print("Filtering extreme prfs")
            mask = mask & (prf_pars['mu'] > 5).values & (prf_pars['mu'] < 28).values

        if mask_by_ips:
            ips_mask = sub.get_surf_mask(roi='ips')
            mask = mask & ips_mask

        mu_vertex = get_alpha_vertex(prf_pars['mu'].values, mask, vmin=5, vmax=vmax, subject=fs_subject) 
        r2_vertex = get_alpha_vertex(prf_pars['r2'].values, mask, cmap='hot', vmin=threshold, vmax=0.25, subject=fs_subject)
        #cvr2_vertex = get_alpha_vertex(prf_pars['cvr2'].values, mask, cmap='hot', vmin=0.0, vmax=0.25, subject=fs_subject)

        vertices[f"sub-{subject}_mu_vertex_session_{session}"] = mu_vertex
        vertices[f"sub-{subject}_r2_vertex_session_{session}"] = r2_vertex
        #vertices[f"cvr2_vertex_session_{session}"] = cvr2_vertex

    vertices = {k: v for k, v in sorted(vertices.items(), key=lambda item: item[0])}
    webgl.show(vertices)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('subject')
    parser.add_argument('--bids_folder', default='/Volumes/mrenkeED/data/ds-stressrisk')
    parser.add_argument('--fsnative', action='store_true')
    parser.add_argument('--key', default=None) # 'encoding_model.denoise.smoothed.natural_space'
    #parser.add_argument('--unsmoothed', dest='smoothed', action='store_false')
    #parser.add_argument('--denoise', action='store_true')
    parser.add_argument('--both_sessions', default=None, action='store_false')
    parser.add_argument('--threshold_r2', dest='use_cvr2', action='store_false')
    parser.add_argument('--threshold', default=None, type=float)
    parser.add_argument('--no_mu_filter', dest='filter_extreme_prfs', action='store_false')
    parser.add_argument('--vmax', default=28, type=float)

    args = parser.parse_args()
    main(args.subject, bids_folder=args.bids_folder,key=args.key,both_sessions = args.both_sessions, use_cvr2=args.use_cvr2, 
         threshold=args.threshold, fsnative=args.fsnative,filter_extreme_prfs=args.filter_extreme_prfs,
         vmax=args.vmax) #

    # smoothed=args.smoothed, 
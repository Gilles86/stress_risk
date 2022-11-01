

import numpy as np
import os.path as op
from nipype.interfaces.freesurfer import SurfaceTransform

ses = 1
bids_folder = '/Users/mrenke/data/ds-stressrisk'
runs = range(1,7)

for sub in range(4,19):
    sub = str(sub).zfill(2)
    for run in runs:
        for hemi in ['L', 'R']:
            sxfm = SurfaceTransform(subjects_dir='/Users/mrenke/data/ds-stressrisk/derivatives/freesurfer')
            in_file = f'sub-{sub}_ses-{ses}_task-risk_run-{run}_space-fsaverage_hemi-{hemi}_bold.func.gii'
            in_file_path = op.join(bids_folder, 'derivatives', 'fmriprep', f'sub-{sub}',f'ses-{ses}','func',in_file)
            out_file = f'sub-{sub}_ses-{ses}_task-risk_run-{run}_space-fsaverage5_hemi-{hemi}_bold.func.gii'
            out_file_path = op.join(bids_folder, 'derivatives', 'fmriprep', f'sub-{sub}',f'ses-{ses}','func',out_file)

            sxfm.inputs.source_file = in_file_path
            sxfm.inputs.out_file = out_file_path

            sxfm.inputs.source_subject = 'fsaverage'
            sxfm.inputs.target_subject = 'fsaverage5'

            if hemi == 'L':
                sxfm.inputs.hemi = 'lh'
            elif hemi == 'R':
                sxfm.inputs.hemi = 'rh'

            r = sxfm.run()
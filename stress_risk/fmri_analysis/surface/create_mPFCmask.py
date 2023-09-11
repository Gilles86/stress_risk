import argparse
import os
import os.path as op
from nipype.interfaces.freesurfer import SurfaceTransform

import numpy as np
from nilearn import surface
from neuropythy.freesurfer import subject as fs_subject
from neuropythy.io import load, save
from neuropythy.mri import (is_image, is_image_spec, image_clear, to_image)



# -----------------------------------------------

def main(subject, bids_folder, roi):
    subjects_dir = op.join(bids_folder, 'derivatives', 'freesurfer') # needed for transform_surface
    target_subject = f'sub-{subject}'
    target_dir = op.join(bids_folder, 'derivatives', f'{roi}_masks', target_subject)

    if not op.exists(target_dir):
        os.makedirs(target_dir)

    # 1. transform from fsaverage to fsnative
    def transform_surface(in_file,
        out_file, 
        target_subject,
        hemi,
        source_subject='fsaverage'):

        sxfm = SurfaceTransform(subjects_dir= subjects_dir)
        sxfm.inputs.source_file = in_file
        sxfm.inputs.out_file = out_file
        sxfm.inputs.source_subject = source_subject
        sxfm.inputs.target_subject = target_subject
        sxfm.inputs.hemi = fs_hemi
        # sxfm.cmdline #helps with debugging 
        r = sxfm.run()
        return r

    for fs_hemi in ['rh','lh']:
        in_file = op.join(bids_folder, f'derivatives/surface_masks/mask_MarsAtlas_mPFC_hemi-{fs_hemi}.gii')
        out_file = op.join(target_dir, f'{target_subject}_space-fsnative_hemi-{fs_hemi}.{roi}.gii')

        transform_surface(in_file, out_file, target_subject, fs_hemi)

    # 2. surface to volume
    ses_anat = 1

    fsnative_fn_L = op.join(target_dir, f'{target_subject}_space-fsnative_hemi-lh.{roi}.gii')
    mask_data_L = surface.load_surf_data(fsnative_fn_L).astype(bool)

    fsnative_fn_R = op.join(target_dir, f'{target_subject}_space-fsnative_hemi-rh.{roi}.gii')
    mask_data_R = surface.load_surf_data(fsnative_fn_R).astype(bool)

    sub = fs_subject(op.join(bids_folder, 'derivatives', 'freesurfer', f'sub-{subject}'))
    im = load(op.join(bids_folder, 'derivatives', 'fmriprep', f'sub-{subject}',f'ses-{ses_anat}',
    'anat', f'sub-{subject}_ses-{ses_anat}_desc-preproc_T1w.nii.gz'))
    im = to_image(image_clear(im, fill=0.0), dtype=np.int)

    print('Generating volume...')

    data = (mask_data_L, mask_data_R)
                
    new_im = sub.cortex_to_image(data,
            im,
            hemi=None,
            method='nearest',
            fill=0.0)

    target_fn = op.join(target_dir, f'sub-{subject}_space-T1w_{roi}_hemi-both.nii.gz')
    save(target_fn, new_im)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('subject', default=None)
    parser.add_argument('--bids_folder', default='/Users/mrenke/data/ds-stressrisk/')
    parser.add_argument('--roi', default ='mpfc')
    args = parser.parse_args()

    main(args.subject,  bids_folder=args.bids_folder, roi = args.roi) 
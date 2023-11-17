import argparse
import cortex
from nilearn import image
import numpy as np
import os.path as op
import nibabel as nib

# visualize in pycoretx r2 maps via Volume or Surface file to make sure they are similar!

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('subject', default=1, nargs='?')
    cmd_args = parser.parse_args()

    sub = cmd_args.subject
    #sub = f'{sub:02}'
    ses = 1
    xfm = 'identity.bold'

    #bids_folder = '/Volumes/mrenkeED/data/ds-stressrisk' # careful, pycortex subs are referrring to fmriprep/freesurfer registration saved on local that is different to the one on /Volumes etc.
    bids_folder = '/Users/mrenke/data/ds-stressrisk'
    
    ses = 1
    base = 'encoding_model.smoothed'
    specification=''

    subject = f'sub-{sub}'

    # from vol
    r2_file_from_vol =  op.join(bids_folder, 'derivatives', base , f'sub-{sub}', f'ses-{ses}', 'func', 
        f'sub-{sub}_ses-{ses}_desc-r2.optim_space-T1w_pars.nii.gz')
    r2_data_from_vol = image.load_img(r2_file_from_vol).get_data().T
    r2_from_vol = cortex.Volume(r2_data_from_vol, subject, xfm)

    # from surf
    r2_file_from_surf_L =  op.join(bids_folder, 'derivatives', base , f'sub-{sub}', f'ses-{ses}', 'func', 
        f'sub-{sub}_ses-{ses}_task-risk_space-fsnative_hemi-lh_r2.surf.gii')
    r2_file_from_surf_R =  op.join(bids_folder, 'derivatives', base , f'sub-{sub}', f'ses-{ses}', 'func', 
        f'sub-{sub}_ses-{ses}_task-risk_space-fsnative_hemi-rh_r2.surf.gii')
    r2_from_surf = cortex.dataset.Vertex(np.concatenate([nib.load(r2_file_from_surf_L).agg_data(), nib.load(r2_file_from_surf_R).agg_data()], axis=0), subject=subject) #

    ips_L =  op.join(bids_folder, 'derivatives', 'ips_masks' , f'sub-{sub}',
         f'sub-{sub}_desc-NPC_L_space-fsnative_hemi-lh.ips.gii')
    ips_R =  op.join(bids_folder, 'derivatives','ips_masks' , f'sub-{sub}',
         f'sub-{sub}_desc-NPC_R_space-fsnative_hemi-rh.ips.gii')
    ips_mask = cortex.dataset.Vertex(np.concatenate([nib.load(ips_L).agg_data(), nib.load(ips_R).agg_data()], axis=0), subject=subject) #

    ds = cortex.Dataset(r2_from_vol=r2_from_vol,
                        r2_from_surf = r2_from_surf,
                        ips_mask = ips_mask
                        ) #somehow does not work to display both in one webshow...."TypeError: byte indices must be integers or slices, not tuple"
                        
    cortex.webshow(ds) 
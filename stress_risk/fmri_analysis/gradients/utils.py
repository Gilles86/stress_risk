import cortex
from nilearn import image
import numpy as np
import os.path as op
import nibabel as nib


def loadGradAsCortexVertex(sub,ses,bids_folder,specification, parcel = '_noParcel'):
    grad_n = 1
    hemi = 'L'
    file = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}',
                f'sub-{sub}_ses-{ses}_task-risk_space-fsnative_hemi-{hemi}_grad{grad_n}{parcel}{specification}.surf.gii')
    im1L = nib.load(file)

    hemi = 'R'
    file = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}',
            f'sub-{sub}_ses-{ses}_task-risk_space-fsnative_hemi-{hemi}_grad{grad_n}{parcel}{specification}.surf.gii')
    im1R = nib.load(file)


    grad_n = 2
    hemi = 'L'
    file = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}',
                f'sub-{sub}_ses-{ses}_task-risk_space-fsnative_hemi-{hemi}_grad{grad_n}{parcel}{specification}.surf.gii')
    im2L = nib.load(file)


    hemi = 'R'
    file = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}',
                f'sub-{sub}_ses-{ses}_task-risk_space-fsnative_hemi-{hemi}_grad{grad_n}{parcel}{specification}.surf.gii')
    im2R = nib.load(file)


    grad1 = cortex.dataset.Vertex(np.concatenate([im1L.agg_data(), im1R.agg_data()], axis=0), subject=subject,cmap='viridis_r' )
    grad2 = cortex.dataset.Vertex(np.concatenate([im2L.agg_data(), im2R.agg_data()], axis=0), subject=subject, cmap='viridis_r')
    return grad1,grad2

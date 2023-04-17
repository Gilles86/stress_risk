# environment: numrefields_copy OR pycortex
import argparse

import cortex
from nilearn import image
import numpy as np
import os.path as op
import nibabel as nib

#from .utils import loadGradAsCortexVertex

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

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('subject', default=1, nargs='?')
    cmd_args = parser.parse_args()

    sub = cmd_args.subject
    #sub = f'{sub:02}'
    ses = 1
    xfm = 'identity.bold'

    bids_folder = '/Users/mrenke/data/ds-stressrisk'
    ses = 1
    base = 'encoding_model.smoothed'
    specification=''

    subject = f'sub-{sub}'

    r2_data =  op.join(bids_folder, 'derivatives', base , f'sub-{sub}', f'ses-{ses}', 'func', 
        f'sub-{sub}_ses-{ses}_desc-r2.optim_space-T1w_pars.nii.gz')
    r2_data = image.load_img(r2_data).get_data().T
    r2_surf = cortex.Volume(r2_data, subject, xfm)

    grad1,grad2 = loadGradAsCortexVertex(sub,ses,bids_folder,specification)

    ds = cortex.Dataset(r2=r2_surf,
                        grad1 = grad1,
                        grad2 = grad2) #somehow does not work to display both in one webshow...."TypeError: byte indices must be integers or slices, not tuple"
                        
    cortex.webshow(ds) 
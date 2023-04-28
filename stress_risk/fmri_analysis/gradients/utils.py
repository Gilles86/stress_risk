#import cortex
from nilearn import image
import numpy as np
import os.path as op
import nibabel as nib
import os
from nilearn import signal
import pandas as pd
from nipype.interfaces.freesurfer import SurfaceTransform # needs the fsaverage & fsaverage5 in ..derivatives/freesurfer folder!


def loadGradAsNpArray(sub,ses,bids_folder,specification, parcel = '_noParcel'): # looping did not work (dont understand why)
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


    grad1 = np.concatenate([im1L.agg_data(), im1R.agg_data()], axis=0)
    grad2 = np.concatenate([im2L.agg_data(), im2R.agg_data()], axis=0)

    return grad1,grad2



def cleanTS(sub, ses, runs = range(1, 7),space = 'fsaverage5', bids_folder='/Users/mrenke/data/ds-stressrisk'):
    # load in data as timeseries and regress out confounds (for each run sepeprately)
    number_of_vertex = 20484  # 'fsaverage5', 10242 * 2

    fmriprep_confounds_include = ['global_signal', 'dvars', 'framewise_displacement', 'trans_x',
                                    'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z',
                                    'a_comp_cor_00', 'a_comp_cor_01', 'a_comp_cor_02', 'a_comp_cor_03', 'cosine00', 'cosine01', 'cosine02'
                                    ] # 

    clean_ts_runs = np.empty([number_of_vertex,0])

    ex_file = op.join(bids_folder,'derivatives', 'fmriprep', f'sub-{sub}', f'ses-{ses}', 'func', 
            f'sub-{sub}_ses-{ses}_task-risk_run-1_space-{space}_hemi-L_bold.func.gii')
    
    if (os.path.exists(ex_file) == False):
        print(f'sub-{sub} fsaverage5.gii missing, fsavTofsav5 will be performed')
        fsavTofsav5(sub,ses, bids_folder)

    for run in runs:
        timeseries = [None] * 2
        for i, hemi in enumerate(['L', 'R']):
            filename = op.join(bids_folder,'derivatives', 'fmriprep', f'sub-{sub}', f'ses-{ses}', 'func', 
            f'sub-{sub}_ses-{ses}_task-risk_run-{run}_space-{space}_hemi-{hemi}_bold.func.gii')
            
            
            timeseries[i] = nib.load(filename).agg_data()
        timeseries = np.vstack(timeseries) # (20484, 135)

        fmriprep_confounds_file = op.join(bids_folder,'derivatives', 'fmriprep', f'sub-{sub}', f'ses-{ses}', 'func', f'sub-{sub}_ses-{ses}_task-risk_run-{run}_desc-confounds_timeseries.tsv')
        fmriprep_confounds = pd.read_table(fmriprep_confounds_file)[fmriprep_confounds_include] 
        fmriprep_confounds= fmriprep_confounds.fillna(method='bfill')

        #clean_ts_list[run] = signal.clean(timeseries.T, confounds=fmriprep_confounds).T
        clean_ts = signal.clean(timeseries.T, confounds=fmriprep_confounds).T

        clean_ts_runs = np.append(clean_ts_runs, clean_ts, axis=1)

    return clean_ts_runs

#%% 

def saveGradToNPFile(grad, sub,ses, specification='',bids_folder='/Users/mrenke/data/ds-stressrisk'):
    target_dir = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}')

    if not op.exists(target_dir):
        os.makedirs(target_dir)

    for g, n_grad  in enumerate([1,2]):
        np.save(op.join(target_dir,f'grad{n_grad}_noParcel{specification}.npy'), grad[g])

def npFileTofs5Gii(sub,ses, specification='',bids_folder='/Users/mrenke/data/ds-stressrisk'):
    target_dir = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}')

    for n_grad in [1,2]:
        grad = np.load(op.join(target_dir, f'grad{n_grad}_noParcel{specification}.npy'))
        grad = np.split(grad,2) # for i, hemi in enumerate(['L', 'R']): --> left first

        for h, hemi in enumerate(['L', 'R']):    

            gii_im_datar = nib.gifti.gifti.GiftiDataArray(data=grad[h])
            gii_im = nib.gifti.gifti.GiftiImage(darrays= [gii_im_datar])

            out_file = op.join(target_dir, f'sub-{sub}_ses-{ses}_task-risk_space-fsaverage5_hemi-{hemi}_grad{n_grad}_noParcel{specification}.surf.gii')
            gii_im.to_filename(out_file) # https://nipy.org/nibabel/reference/nibabel.spatialimages.html


# nipype transformations

def fsav5Tofsnative(sub,ses, specification='', bids_folder='/Users/mrenke/data/ds-stressrisk'):

    target_space = 'fsnative'

    for n_grad in [1,2]:

        for i, hemi in enumerate(['L', 'R']):   

            sxfm = SurfaceTransform(subjects_dir=op.join
            (bids_folder,'derivatives','freesurfer'))

            grad_sub_dir = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}')

            in_file = op.join(grad_sub_dir, f'sub-{sub}_ses-{ses}_task-risk_space-fsaverage5_hemi-{hemi}_grad{n_grad}_noParcel{specification}.surf.gii')
            out_file = op.join(grad_sub_dir, f'sub-{sub}_ses-{ses}_task-risk_space-{target_space}_hemi-{hemi}_grad{n_grad}_noParcel{specification}.surf.gii')

            sxfm.inputs.source_file = in_file
            sxfm.inputs.out_file = out_file

            sxfm.inputs.source_subject = 'fsaverage5'
            sxfm.inputs.target_subject = f'sub-{sub}'

            if hemi == 'L':
                sxfm.inputs.hemi = 'lh'
            elif hemi == 'R':
                sxfm.inputs.hemi = 'rh'

            r = sxfm.run()


def fsavTofsav5(sub,ses, bids_folder='/Users/mrenke/data/ds-stressrisk'):
    runs = range(1,7)

    for run in runs:
        for hemi in ['L', 'R']:
            sxfm = SurfaceTransform(subjects_dir=op.join(bids_folder,'derivatives','freesurfer'))
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

def fsav5Tofsav(sub,ses, specification='',bids_folder='/Users/mrenke/data/ds-stressrisk'):

    target_space = 'fsaverage'

    for n_grad in [1,2]:

        for i, hemi in enumerate(['L', 'R']):   

            sxfm = SurfaceTransform(subjects_dir=op.join
            (bids_folder,'derivatives','freesurfer'))

            grad_sub_dir = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}')

            in_file = op.join(grad_sub_dir, f'sub-{sub}_ses-{ses}_task-risk_space-fsaverage5_hemi-{hemi}_grad{n_grad}_noParcel{specification}.surf.gii')
            out_file = op.join(grad_sub_dir, f'sub-{sub}_ses-{ses}_task-risk_space-{target_space}_hemi-{hemi}_grad{n_grad}_noParcel{specification}.surf.gii')

            sxfm.inputs.source_file = in_file
            sxfm.inputs.out_file = out_file

            sxfm.inputs.source_subject = 'fsaverage5'
            sxfm.inputs.target_subject = 'fsaverage'

            if hemi == 'L':
                sxfm.inputs.hemi = 'lh'
            elif hemi == 'R':
                sxfm.inputs.hemi = 'rh'

            r = sxfm.run()
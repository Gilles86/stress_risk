import argparse
import os
#import pingouin
import numpy as np
import os.path as op
import pandas as pd
from nilearn import surface
from braincoder.optimize import ResidualFitter
from braincoder.models import GaussianPRF
from braincoder.utils import get_rsq
import numpy as np
from stress_risk.utils import Subject
from braincoder.models import GaussianPRF
from braincoder.optimize import ParameterFitter
from nilearn import image
from nilearn.maskers import NiftiMasker

# needs:
# encoding_model.cv.denoise/../ses-1; vor CV voxel selection
# encoding_model.denoise/../ses-1 ; 
# ginel-trial-estimates: glm_stim1.denoise/../ses-1 & ses-2 ! ; 
# paradigm: ..run-..events.txt ses1 & ses-2
# IPS-mask

stimulus_range = np.linspace(0, 6, 1000)
space = 'T1w'

def main(subject,  smoothed, pca_confounds, bids_folder='/data', #session,
denoise=False, retroicor=False, roi='NPC_R'):
    
    session1 = 1
    target_dir = op.join(bids_folder, 'derivatives', 'decoded_pdfs.volume.svoxels.ses1-en_ses2-de')

    key =  'encoding_model.cv'

    if denoise:
        target_dir += '.denoise'
        key += '.denoise'

    if smoothed:
        target_dir += '.smoothed'

    if (retroicor) and (not denoise):
        raise Exception("When not using GLMSingle RETROICOR is *always* used!")

    if retroicor:
        target_dir += '.retroicor'
        key += '.retroicor'

    if pca_confounds:
        target_dir += '.pca_confounds'

    target_dir = op.join(target_dir, f'sub-{subject}', 'func')

    if not op.exists(target_dir):
        os.makedirs(target_dir)

    sub = Subject(subject, bids_folder)

    # get behavioral and glm-single-trial-estim data from ses1&ses2 as train and test
    paradigm1 = sub.get_behavior(sessions=1, drop_no_responses=False)
    paradigm1['log(n1)'] = np.log(paradigm1['n1'])
    paradigm1 = paradigm1.droplevel(['subject', 'session'])
    paradigm1 = paradigm1['log(n1)']

    paradigm2 = sub.get_behavior(sessions=2, drop_no_responses=False)
    paradigm2['log(n1)'] = np.log(paradigm2['n1'])
    paradigm2 = paradigm2.droplevel(['subject', 'session'])
    paradigm2 = paradigm2['log(n1)']

    data1 = sub.get_single_trial_volume(1, roi=roi, smoothed=smoothed, pca_confounds=pca_confounds, denoise=denoise, retroicor=retroicor).astype(np.float32)
    data1.index = paradigm1.index

    data2 = sub.get_single_trial_volume(2, roi=roi, smoothed=smoothed, pca_confounds=pca_confounds, denoise=denoise, retroicor=retroicor).astype(np.float32)
    data2.index = paradigm2.index

    train_data, train_paradigm = data1.copy(), paradigm1.copy() # train with sesssion 1
    test_data, test_paradigm = data2.copy(), paradigm2.copy() # test with session 2

    # get average cv-r2 map from seesion 1 for voxel selection
    fn = op.join(bids_folder, 'derivatives', key, f'sub-{subject}', f'ses-{session1}','func', f'sub-{subject}_ses-{session1}_desc-cvr2.optim_space-T1w_pars.nii.gz')
    im_cvr2 = image.load_img(fn)

    mask = sub.get_volume_mask(roi=roi, session=1, epi_space=True) # anat from session1
    masker = NiftiMasker(mask_img=mask)

    cv_r2 = pd.DataFrame(masker.fit_transform(im_cvr2))
    r2_mask = cv_r2 > 0.0
    r2_mask = r2_mask.to_numpy().T
    n_voxels = r2_mask.sum()

    # filter data wtih r2-mask
    train_data = train_data.loc[:, r2_mask]
    test_data = test_data.loc[:, r2_mask]

    pars = sub.get_prf_parameters_volume(session=1, cross_validated=False,
        denoise=denoise, retroicor=retroicor,
        smoothed=smoothed, pca_confounds=pca_confounds,
        roi=roi)

    model = GaussianPRF(parameters=pars)

    model.apply_mask(r2_mask)
    model.init_pseudoWWT(stimulus_range, model.parameters)
    
    # train
    residfit = ResidualFitter(model, train_data,
                                train_paradigm.astype(np.float32))

    omega, dof = residfit.fit(init_sigma2=10.0,
            method='t',
            max_n_iterations=10000)

    print('DOF', dof)

    bins = stimulus_range.astype(np.float32)
    # test
    pdf = model.get_stimulus_pdf(test_data, bins,
            model.parameters,
            omega=omega,
            dof=dof)

    print(pdf)

    E = (pdf * pdf.columns).sum(1) / pdf.sum(1)

    target_fn = op.join(target_dir, f'sub-{subject}_ses1-en_ses2-de_mask-{roi}_nvoxels-{n_voxels}_space-{space}_pars.tsv')
    pdf.to_csv(target_fn, sep='\t')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('subject', default=None)
    #parser.add_argument('session', default=None)
    parser.add_argument('--bids_folder', default='/data')
    parser.add_argument('--smoothed', action='store_true')
    parser.add_argument('--pca_confounds', action='store_true')
    parser.add_argument('--denoise', action='store_true')
    parser.add_argument('--retroicor', action='store_true')
    parser.add_argument('--mask', default='NPC_R')
    args = parser.parse_args()

    main(args.subject,  args.smoothed, args.pca_confounds, #args.session,
            denoise=args.denoise,
            retroicor=args.retroicor,
            bids_folder=args.bids_folder, roi=args.mask)
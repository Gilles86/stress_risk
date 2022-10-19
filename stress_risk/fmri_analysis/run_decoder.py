

import argparse
import os
import pingouin
import numpy as np
import os.path as op
import pandas as pd
from nilearn import surface
from braincoder.optimize import ResidualFitter
from braincoder.models import GaussianPRF
from braincoder.utils import get_rsq
from utils import get_volume_mask, get_single_trial_volume, get_prf_parameters_volume
import numpy as np


def main(subject, session, bids_folder='/Users/mrenke/data/ds-stressrisk', smoothed=True, n_voxels = 250, mask = 'NPC_R', space = 'T1w', 
        pca_confounds=False):
    
    stimulus_range = np.linspace(0, 6, 1000)
    # stimulus_range = np.log(np.arange(400))
    #mask = 'wang15_ips'
    N_runs = 6 #the way python counts

    target_dir = op.join(bids_folder, 'derivatives', 'decoded_pdfs.volume')

    if smoothed:
        target_dir += '.smoothed'

    if pca_confounds:
        target_dir += '.pca_confounds'

    target_dir = op.join(target_dir, f'sub-{subject}')

    if not op.exists(target_dir):
        os.makedirs(target_dir)
    
    #%%

    paradigm = [pd.read_csv(op.join(bids_folder, f'sub-{subject}', f'ses-{session}',
                                    'func', f'sub-{subject}_ses-{session}_task-risk_run-{run}_events.tsv'), sep='\t')
                for run in range(1, N_runs+1)]

    paradigm = pd.concat(paradigm, keys=range(1, N_runs+1), names=['run'])

    paradigm = paradigm[paradigm.trial_type ==
                        'stimulus 1'].set_index('trial_nr', append=True)

    paradigm['log(n1)'] = np.log(paradigm['n1'])

    #paradigm = paradigm.droplevel(['subject', 'session'])                                  

    data = get_single_trial_volume(subject, session, bids_folder=bids_folder, mask=mask, smoothed=smoothed, pca_confounds=pca_confounds).astype(np.float32)
    data.index = paradigm.index
    print(data) # 120 (trials) x 976 (Voxels inside IPS mask)

    pdfs = []
    runs = range(1, N_runs+1)

    for test_run in runs:

        test_data, test_paradigm = data.loc[test_run].copy(), paradigm.loc[test_run].copy()
        train_data, train_paradigm = data.drop(test_run, level='run').copy(), paradigm.drop(test_run, level='run').copy()

        pars = get_prf_parameters_volume(subject, session, cross_validated=True,
                smoothed=smoothed, pca_confounds=pca_confounds,
                run=test_run, mask=mask, bids_folder=bids_folder)
        # pars = get_prf_parameters_volume(subject, session, cross_validated=False,  mask=mask, bids_folder=bids_folder)
        print(pars) # volumes from CV-fit_trials, masked by IPS, keys = ['mu', 'sd', 'amplitude', 'baseline'] concatenated


        model = GaussianPRF(parameters=pars)
        pred = model.predict(paradigm=train_paradigm['log(n1)'].astype(np.float32))

        r2 = get_rsq(train_data, pred)
        print(r2.describe())
        r2_mask = r2.sort_values(ascending=False).index[:n_voxels] # take n_voxels best voxels

        train_data = train_data[r2_mask]
        test_data = test_data[r2_mask]

        print(r2.loc[r2_mask])
        model.apply_mask(r2_mask)

        model.init_pseudoWWT(stimulus_range, model.parameters)
        residfit = ResidualFitter(model, train_data,
                                    train_paradigm['log(n1)'].astype(np.float32))

        omega, dof = residfit.fit(init_sigma2=10.0,
                method='t',
                max_n_iterations=10000)

        print('DOF', dof)

        bins = stimulus_range.astype(np.float32)

        pdf = model.get_stimulus_pdf(test_data, bins, #prob dens func 
                model.parameters,
                omega=omega,
                dof=dof)


        print(pdf)
        E = (pdf * pdf.columns).sum(1) / pdf.sum(1) # expected value --> presented stimulus

        print(pd.concat((E, test_paradigm['log(n1)']), axis=1))
        print(pingouin.corr(E, test_paradigm['log(n1)']))

        pdfs.append(pdf)

    # after loop bring all together
    pdfs = pd.concat(pdfs)

    target_fn = op.join(target_dir, f'sub-{subject}_ses-{session}_mask-{mask}_nvoxels-{n_voxels}_space-{space}_pars.tsv')
    pdfs.to_csv(target_fn, sep='\t')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('subject', default=None)
    parser.add_argument('session', default=None)
    parser.add_argument('--bids_folder', default='/Users/mrenke/data/ds-stressrisk')
    parser.add_argument('--smoothed', action='store_true')
    parser.add_argument('--pca_confounds', action='store_true')
    parser.add_argument('--n_voxels', default= 250)
    parser.add_argument('--mask', default= 'NPC_R')
    parser.add_argument('--space', default = 'T1w')
    args = parser.parse_args()

    main(args.subject, args.session, bids_folder=args.bids_folder, smoothed=args.smoothed, n_voxels = args.n_voxels, 
            pca_confounds=args.pca_confounds)

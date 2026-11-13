import os
import os.path as op
import argparse
from stress_risk.utils.data import Subject
from tqdm.contrib.itertools import product
import pandas as pd
import numpy as np

def main(roi='NPCr', bids_folder='/data/ds-stressrisk', smoothed=True, old_models=False):

    key = 'summary_encoding_models'

    if old_models:
        key += '.old'

    if smoothed:
        key += '.smoothed'

    print(key)

    target_dir = op.join(bids_folder, 'derivatives', key)
    print(f'Writing to {target_dir}')
    os.makedirs(target_dir, exist_ok=True)

    subject_ids = range(1, 62)

    subjects = [Subject(subject=subject_id) for subject_id in subject_ids]
    pars = []

    if not old_models:
        model_labels = range(0, 3)
    else:
        model_labels = [None]

    keys = []
    
    if old_models:
        for sub in subjects:
            try:
                roi, smoothed = 'NPC_R', True
                p1 = sub.get_prf_parameters_volume(smoothed=smoothed, roi=roi, session=1, retroicor=True, denoise=True, cross_validated=False, run=None)
                p2 = sub.get_prf_parameters_volume(smoothed=smoothed, roi=roi, session=2, retroicor=True, denoise=True, cross_validated=False, run=None)
                p = pd.concat([p1, p2], keys=[1., 2.], names=['session'], axis=1)
                p.columns.names = ['session', 'parameter']

                p = p.reorder_levels(['parameter', 'session'], axis=1).sort_index(axis=1, level=0)
                p[('mu_natural', 1)], p[('mu_natural', 2)] = np.exp(p[('mu', 1)]), np.exp(p[('mu', 2)])

                p[('cvr2', 'nan')] = p['cvr2'].mean(axis=1)
                p[('r2', 'nan')] = p['r2'].mean(axis=1)

                pars.append(p)
                print(pars[-1].head())
                keys.append((sub.subject))
            except Exception as e:
                # raise e
                print(f"Failed for {sub.subject}: {e}")

        pars = pd.concat(pars, keys=keys, names=['subject_id'])
    else:
        for sub, model_label in product(subjects, model_labels):
            try:
                if old_models:
                    # pars.append(sub.get_prf_parameters_volume(smoothed=smoothed, roi='NPCr'))
                    raise NotImplementedError("Old models not implemented")
                else:
                    p = sub.get_prf_parameters_volume2(smoothed=smoothed, model_label=model_label, roi=roi)
                    p[('mu_natural', 1)], p[('mu_natural', 2)] = np.exp(p[('mu', 1)]), np.exp(p[('mu', 2)])
                    pars.append(p)
                    print(pars[-1].head())
                keys.append((sub.subject, model_label))
            except Exception as e:
                # raise e
                print(f"Failed for {sub.subject}: {e}")

        pars = pd.concat(pars, keys=keys, names=['subject_id', 'model_label'])

    # pars.columns.names = ['parameter', 'session']
    pars.to_csv(op.join(target_dir, f'group_roi-{roi}_parameters.tsv'), sep='\t')

argparser = argparse.ArgumentParser()
argparser.add_argument('roi', default='NPC_R', type=str)
argparser.add_argument('--bids_folder', default='/data/ds-stressrisk')
argparser.add_argument('--smoothed', action='store_true')
argparser.add_argument('--old_models', action='store_true', dest='old_models')

if __name__ == '__main__':
    args = argparser.parse_args()
    main(roi=args.roi, bids_folder=args.bids_folder, smoothed=args.smoothed, old_models=args.old_models)
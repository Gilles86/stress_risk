# add event of piechart presentation for regresing out all task events (gradient analysis)
# from experiment/gamble.py
#         elif self.phase == 2:
#            self.piechart1.draw()
#         elif self.phase == 6:
#            self.piechart2.draw()


import os
import os.path as op
import argparse
import pandas as pd
import numpy as np
from nilearn import image


def main(subject, session, source_bids_folder, target_bids_folder, max_rt=1.0):

    sourcedata = op.join(source_bids_folder, 'sourcedata')

    target_dir = op.join(target_bids_folder, f'sub-{subject}', f'ses-{session}', 'func')
    
    if not op.exists(target_dir):
        os.makedirs(target_dir)

    for run in range(1, 7):
        print(subject, session, run)
        nii = op.join(target_dir, f'sub-{subject}_ses-{session}_task-risk_run-{run}_bold.nii')
        print(nii)

        if op.exists(nii):
            n_volumes = image.load_img(nii).shape[-1]
        else:
            n_volumes = 135


        behavior = pd.read_table(op.join(sourcedata, f'behavior/sub-{subject}/ses-{session}/sub-{subject}_ses-{session}_task-task_run-{run}_events.tsv'))
        behavior['trial_nr'] = behavior['trial_nr'].astype(int)

        # print(behavior)

        pulses = behavior[behavior.event_type == 'pulse'][['trial_nr', 'onset']]

        pulses['ipi'] = pulses['onset'].diff()
        pulses = pulses[((pulses['ipi'] > 1.) & (pulses['ipi'] < 5.)) | pulses.ipi.isnull()]
        print(pulses.sort_values('ipi')['ipi'])

        if n_volumes != pulses.shape[0]:
            pulses = pulses.set_index(np.arange(1, pulses.shape[0]+1))[['trial_nr', 'onset']]
            t0 = pulses.loc[1, 'onset'] - (n_volumes - pulses.shape[0]) * 2.3
            print(f'******Pulse missing: {pulses.loc[1, "onset"]}, {t0} ({pulses.shape[0]})*******')
        else:
            pulses = pulses.set_index(np.arange(1, n_volumes+1))[['trial_nr', 'onset']]
            t0 = pulses.loc[1, 'onset']
            print(t0)


        stim1_dots = behavior[(behavior['event_type'] == 'stim') & (behavior['phase'] == 4)].copy()
        stim1_dots['n'] = stim1_dots['n1']
        stim1_dots['onset'] -= t0
        stim1_dots['trial_type'] = 'stim1 dots'


        stim2_dots = behavior[(behavior['event_type'] == 'stim') & (behavior['phase'] == 8)].copy()
        stim2_dots['n'] = stim2_dots['n2']
        stim2_dots['onset'] -= t0
        stim2_dots['trial_type'] = 'stim2 dots'

        # also the stimulus of probability presentaion as piechart
        stim1_prob = behavior[(behavior['event_type'] == 'stim') & (behavior['phase'] == 2)].copy()
        stim1_prob['prob'] = stim1_prob['prob1']
        stim1_prob['onset'] -= t0
        stim1_prob['trial_type'] = 'stim1 prob'


        stim2_prob = behavior[(behavior['event_type'] == 'stim') & (behavior['phase'] == 6)].copy()
        stim2_prob['prob'] = stim2_prob['prob2']
        stim2_prob['onset'] -= t0
        stim2_prob['trial_type'] = 'stim2 prob'

        choice = behavior[(behavior['event_type'] == 'choice')].copy()
        choice['onset'] -= t0
        choice['trial_type'] = 'choice'

        events = pd.concat((stim1_dots, stim1_prob,stim2_dots, stim2_prob, choice)).sort_index().reset_index(drop=True)
        # result['choice'] = result['choice'].astype(int)
        events = events[['trial_nr', 'onset', 'trial_type', 'prob1', 'prob2', 'n1', 'n2', 'n', 'prob','choice']]

        fn = op.join(target_dir, f'sub-{subject}_ses-{session}_task-risk_run-{run}_events_allEvents.tsv')
        events.to_csv(fn, index=False, sep='\t')


def get_hazard(x, s=1.0, loc=0.0, scale=10, cut=30, use_cut=False):
    import scipy.stats as ss
    
    x = x / .7

    dist = ss.lognorm(s, loc, scale)
    
    if use_cut:
        sf = lambda x: 1 - (dist.cdf(x) / dist.cdf(cut))
    else:
        sf = dist.sf

    return np.clip(dist.pdf(x) / sf(x), 0, np.inf)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('subject', default=None)
    parser.add_argument('--session', default=1)
    parser.add_argument('--source_bids_folder', default='/Users/mrenke/data/ds-stressrisk')
    parser.add_argument('--target_bids_folder', default='/Volumes/mrenkeED/data/ds-stressrisk')

    args = parser.parse_args()

    main(args.subject, args.session, args.source_bids_folder, args.target_bids_folder)

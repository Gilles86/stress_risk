#%%
import os.path as op
from re import I
import pandas as pd
from itertools import product
import numpy as np
import pkg_resources
#import yaml
from sklearn.decomposition import PCA

#%%
class Subject(object):

    def __init__(self, subject, bids_folder='/Users/mrenke/data/ds-stressrisk'):

        self.subject = '%02d' % int(subject)
        self.bids_folder = bids_folder
    

    def get_behavior(self, bids_folder='/Users/mrenke/data/ds-stressrisk'):
        session=1
        runs = range(1, 7)
        df = []
        for run in runs:

            fn = op.join(self.bids_folder, f'sub-{self.subject}/ses-{session}/func/sub-{self.subject}_ses-{session}_task-task_run-{run}_events.tsv')

            if op.exists(fn):
                d = pd.read_csv(fn, sep='\t',
                            index_col=['trial_nr', 'trial_type'])
                d['subject'], d['session'], d['run'] = int(self.subject), session, run
                df.append(d)

        if len(df) > 0:
            df = pd.concat(df)
            df = df.reset_index().set_index(['subject', 'session', 'stimulation_condition', 'run', 'trial_nr', 'trial_type']) 
            df = df.unstack('trial_type')
            return self._cleanup_behavior(df)
        else:
            return pd.DataFrame([])

    def _cleanup_behavior(df_):
        df = df_[[]].copy()
        df['rt'] = df_.loc[:, ('onset', 'choice')] - df_.loc[:, ('onset', 'stimulus 2')]
        df['n1'], df['n2'] = df_['n1']['stimulus 1'], df_['n2']['stimulus 1']
        df['prob1'], df['prob2'] = df_['prob1']['stimulus 1'], df_['prob2']['stimulus 1']

        df['choice'] = df_[('choice', 'choice')]
        df['risky_first'] = df['prob1'] == 0.55
        df['chose_risky'] = (df['risky_first'] & (df['choice'] == 1.0)) | (~df['risky_first'] & (df['choice'] == 2.0))
        df.loc[df.choice.isnull(), 'chose_risky'] = np.nan


        df['n_risky'] = df['n1'].where(df['risky_first'], df['n2'])
        df['n_safe'] = df['n2'].where(df['risky_first'], df['n1'])
        df['frac'] = df['n_risky'] / df['n_safe']
        df['log(risky/safe)'] = np.log(df['frac'])

        df = df[~df.chose_risky.isnull()]
        df['chose_risky'] = df['chose_risky'].astype(bool)

#%%
sub_behav = Subject(1)
df = sub_behav.get_behavior()
#%%

        def get_risk_bin(d):
            try: 
                return pd.qcut(d, 6, range(1, 7))
            except Exception as e:
                n = len(d)
                ix = np.linspace(1, 7, n, False)

                d[d.sort_values().index] = np.floor(ix)
                
                return d
        df['bin(risky/safe)'] = df.groupby(['subject'])['frac'].apply(get_risk_bin)

        return df.droplevel(-1, 1)

#%%






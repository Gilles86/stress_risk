#%%
import pandas as pd
import os.path as op
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

bids_folder='/Users/mrenke/data/ds-stressrisk'
target_folder = op.join(bids_folder,'plots_and_ims', 'behavior_analysis', 'logReg_plots')

sub_list_s = list(range(21,27+1))

sub_list= []
for e in sub_list_s:
    sub_list.append(str(e).zfill(2))

ses = 1 
#%%
def get_task_behavior(subject, session, bids_folder='/Users/mrenke/data/ds-stressrisk'):

    runs = range(1, 7)

    df = []

    for run in runs:
        d = pd.read_csv(op.join(bids_folder, f'sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-risk_run-{run}_events.tsv'), sep='\t')
        #d = d[np.in1d(d.phase, [8,9])]
        d['trial_nr'] = d['trial_nr'].astype(int)
        d = d.pivot_table(index=['trial_nr'], values=['choice', 'n1', 'n2', 'prob1', 'prob2'])
        d['task'] = 'task'
        d['log(n1)'] = np.log(d['n1'])
        d['subject'], d['session'], d['run'] = subject, session, run
        d = d.set_index(['subject', 'session', 'run'], append=True).reorder_levels(['subject', 'session', 'run', 'trial_nr'])
        df.append(d)    
    
    df = pd.concat(df)
    
    df['log(risky/safe)'] = np.log(df['n1'] / df['n2'])
    ix = df.prob1 == 1.0

    df.loc[~ix, 'log(risky/safe)'] = np.log(df.loc[~ix, 'n1'] / df.loc[~ix, 'n2'])
    df.loc[ix, 'log(risky/safe)'] = np.log(df.loc[ix, 'n2'] / df.loc[ix, 'n1'])

    df['risky/safe'] = np.exp(df['log(risky/safe)'])

    df.loc[~ix, 'chose_risky'] = df.loc[~ix, 'choice'] == 1
    df.loc[ix, 'chose_risky'] = df.loc[ix, 'choice'] == 2
    df.loc[df.choice.isnull(), 'chose_risky'] = np.nan
    df['chose_risky'] = df['chose_risky'].astype(np.float)
    #df['chose_risky'] = df['chose_risky'].astype(bool)
    df['risky_first'] = df.prob1 == 0.55

    df.loc[df.risky_first, 'base_number'] = df['n2']
    df.loc[~df.risky_first, 'base_number'] = df['n1']

    return df

# %%

for sub in sub_list:
    try: 
        df = get_task_behavior(sub,ses)
        sns.lmplot('log(risky/safe)', 'chose_risky', data=df, logistic=True)

        plt.axhline(.5, c='k', ls='--')
        plt.axvline(np.log(1/.55), c='k', ls='--')

        plt.savefig(op.join(target_folder,f'sub-{sub}_ses-1.png' ))
    except:
        print([sub, 'makes problems'])

# %%

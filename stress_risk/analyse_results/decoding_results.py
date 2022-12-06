
#%% numrefields_copy2 - shouls also work with numrefields
import pandas as pd
import os.path as op
import numpy as np
from stress_risk.utils.data import get_all_behavior
from tqdm.contrib.itertools import product
import matplotlib.pyplot as plt
import pingouin
import seaborn as sns

bids_folder = '/Users/mrenke/data/ds-stressrisk'
# %%
def get_decoding_info(subject, session, pca_confounds=False, denoise=True, smoothed=False, bids_folder=bids_folder, mask='NPC_R', n_voxels=100):

    key = 'decoded_pdfs.volume'

    subject = f'{subject:02d}'

    if denoise:
        key += '.denoise'

    if smoothed:
        key += '.smoothed'

    if pca_confounds and not denoise:
        key += '.pca_confounds'

    pdf = op.join(bids_folder, 'derivatives', key, f'sub-{subject}', 'func', f'sub-{subject}_ses-{session}_mask-{mask}_nvoxels-{n_voxels}_space-T1w_pars.tsv')

    if op.exists(pdf):
        pdf = pd.read_csv(pdf, sep='\t', index_col=[0])
        pdf.columns = pdf.columns.astype(float)

        E = (pdf*pdf.columns.values[np.newaxis, :] / pdf.sum(1).values[:, np.newaxis]).sum(1)

        E = pd.concat((E,), keys=[(int(subject), int(session), 'pca_confounds' if pca_confounds else 'no pca', 'GLMstim' if denoise else "glm", 'smoothed' if smoothed else 'not smoothed', mask, n_voxels)],
        names=['subject', 'session', 'pca', 'glm', 'smoothed', 'mask', 'n_voxels']).to_frame('E')

        return E
    else:
        print(pdf)
        return pd.DataFrame(np.zeros((0, 0)))
# %%


#subjects = list(range(1, 49)) + [116, 150, 141, 152, 130, 163, 165]
subjects = list([55,56,57,58,59])
sessions = [1]
pca_confounds = [True]
denoise = [True]
smoothed = [False]
mask = ['NPC_R']
n_voxels = [50, 100, 250]

pred = []
for sub in subjects:
    pred.append(get_decoding_info(sub, session))


# %%
df = get_all_behavior(drop_no_responses=False, bids_folder = bids_folder)
df.index.unique('subject')
df_ = df.loc[subjects]
df_.index.unique('subject')


# %%
pred = pd.concat(pred)
pred.index.unique(level='subject')

# %%
pred = pred.join(df, how='inner')

#%%
r2_ = pred.groupby('subject').apply(lambda d: pingouin.corr(d['E'], d['log(n1)']))
r2 = r2_.groupby('subject').mean() #subject, n_trials, r,p-val, power

r_final = r2[['r']]

r_final.to_csv('~/data/ds-stressrisk/derivatives/decoding_accuracy_ses-1_sub55-59.tsv', sep='\t')

rnp = pd.read_csv('/Users/mrenke/git/stress_risk/stress_risk/subject_selection/subjectwise_rnp.tsv', sep='\t', index_col=0)
gamma = pd.read_csv('/Users/mrenke/git/stress_risk/stress_risk/subject_selection/subjectwise_gamma.tsv', sep='\t', index_col=0)

r_final = r_final.join(rnp)

r_final.to_csv('subject_stats_sub55-59.tsv', sep='\t')
# %%
df.loc[[56, 57]].xs(1, 0, 'session').xs(1, 0, 'trial')
# %%

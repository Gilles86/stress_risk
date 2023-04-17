#%% 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os.path as op
from stress_risk.behavior.utils import get_data, build_model #, plot_ppc
import os
bids_folder = '/Users/mrenke/data/ds-stressrisk'

model_folder = op.join(bids_folder, 'derivatives', 'cogmodels')

# %%

df_wm = pd.read_excel('/Users/mrenke/data/ds-stressrisk/addMeasures/data_combined.xlsx')
df_pan = pd.read_csv('/Users/mrenke/data/ds-stressrisk/addMeasures/AllRunsSummary.csv')

df_w = pd.DataFrame({'subject' : df_wm['SUBID'], 'wm_begin': np.asarray(df_wm['WM_score_begin']).astype(float), 'wm_end': np.asarray(df_wm['WM_score_end']).astype(float)})
df_p = pd.DataFrame({'subject' : np.asarray(df_pan['Subject ID']).astype(int), 'weber_fraction': np.asarray(df_pan['Weber Fraction']).astype(float)})
df_p = df_p.drop_duplicates(subset='subject', keep='last')

df_decod = pd.read_csv('~/data/ds-stressrisk/derivatives/decoding_accuracy_allSub_allSes.tsv')
#%%
df = df_w.set_index('subject').join(df_p.set_index('subject'))
df['wm_mean'] = (df['wm_begin']+df['wm_end'])/2

# %%
import arviz as az
n_model = 1
idata= az.from_netcdf(op.join(model_folder, f'model-{n_model}_trace.netcdf'))

# %%

def softplus_np(x): return np.log1p(np.exp(-np.abs(x))) + np.maximum(x, 0)

n1_evidence_posterior = idata.posterior['n1_evidence_sd'].to_dataframe()
d1 = n1_evidence_posterior.reset_index()
df_n1= softplus_np(d1[d1['n1_evidence_sd_regressors'] == 'Intercept'].groupby('subject').mean())

n2_evidence_posterior = idata.posterior['n2_evidence_sd'].to_dataframe()
d2 = n2_evidence_posterior.reset_index()
df_n2 = softplus_np(d2[d2['n2_evidence_sd_regressors'] == 'Intercept'].groupby('subject').mean())

df = df.join(df_n2['n2_evidence_sd']).join(df_n1['n1_evidence_sd'])

# %%
from itertools import product

target_folder =op.join(model_folder,'figures',str(n_model),'add-measure_corr')
if not op.exists(target_folder):
    os.makedirs(target_folder)


for (x,y) in product(['n1_evidence_sd', 'n2_evidence_sd'],['wm_mean','weber_fraction'] ):
    c = np.round(stats.pearsonr(df[x],df[y]), 3)
    sns.lmplot(x=x, y=y, data = df)
    plt.title(f'corr: r = {c[0]}, p = {c[1]}')
    plt.savefig(op.join(target_folder, f'corr-plot_{x}_{y}.pdf'), bbox_inches='tight')
    plt.close

# %%

df_probit_params = pd.read_csv('/Users/mrenke/data/ds-stressrisk/derivatives/cogmodels/param_estimates/bambi-1_subseswise_params.csv')
df_pp = df_probit_params[df_probit_params['session']==1]

df = df.join(df_pp.set_index('subject')[['rnp','gamma','intercept']])
# %%
for (x,y) in product(['n1_evidence_sd', 'n2_evidence_sd'],['gamma','rnp', 'intercept'] ):
    c = np.round(stats.pearsonr(df[x],df[y]), 3)
    sns.lmplot(x=x, y=y, data = df)
    plt.title(f'corr: r = {c[0]}, p = {c[1]}')
    plt.savefig(op.join(target_folder, f'corr-plot_{x}_{y}.pdf'), bbox_inches='tight')
    plt.close
# %%
df.to_csv(op.join('/Users/mrenke/data/ds-stressrisk/derivatives/cogmodels/param_estimates','full_params_bambi1_NLC1.csv'))
# %%

#%%
# 
import glob
import re
import pandas as pd



# %% conditions assignec --> sub with session 2!
df_cond = pd.read_csv('/Users/mrenke/data/ds-stressrisk/StressRiskNum_ConditionAssigned.csv')
# %%
df_fMRI = pd.read_csv('/Users/mrenke/git/stress_risk/stress_risk/prepare/fmri_files_df_scloud.tsv')
# %%

for i in range(0, len(df_cond)):
    #df_fMRI.columns[]
    df_fMRI['Unnamed: 0'] == df_cond['SUBID'][i]
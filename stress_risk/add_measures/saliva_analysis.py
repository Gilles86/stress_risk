#%%

import pandas as pd
import numpy as np
import os.path as op

#%%

data_path = '/Users/mrenke/Desktop/StressRisk/2022-StressRisk/Data-Final/Saliva'

df_r = pd.read_excel(op.join(data_path,'salivaResults_clean.xlsx'))
df_a = pd.read_csv(op.join(data_path,'StressRiskNum_subject-scanning_SalivaSamples.csv'))# sample subject assignment from google table: StressRiskNum - subject scanning

# %%
df_a['Sample ID'] = df_a['Salivette #']
df = df_r.set_index('Sample ID').join(df_a.set_index('Sample ID'))
df_r.set_index('Sample ID').join(df_a.set_index('Sample ID')['Subject #'])

sid = []
for i in range(0,len(df)):
    sid.append(np.mod(df.index[i],6))
sid = np.array(sid)
sid[sid == 0] = 6
df['sid'] = sid

df['cortisol_mean'] = df[['Cortisol nmol/l','Cortisol nmol/l.1'] ].mean(axis=1)

#%%
import seaborn as sns
import matplotlib.pyplot as plt


fac = sns.FacetGrid(df,
                    col='Treatment',
                    hue='Subject #',##
                    )
fac.map(plt.plot, 'sid','cortisol_mean')


plt.scatter(df[df['Treatment']==0]['sid'],df[df['Treatment']==0]['cortisol_mean'])
plt.scatter(df[df['Treatment']==1]['sid'],df[df['Treatment']==1]['cortisol_mean'])

#%%
from sklearn import metrics

df_ = df.dropna()
cort_auc = []
for sub in df_['Subject #'].unique():
    ind = df_['Subject #'] == sub
    cort_auc.append(metrics.auc(df_[ind]['sid'],df_[ind]['cortisol_mean'])) # calculates the auc for the 


# %%

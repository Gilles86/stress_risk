# env: behav_fit

#%%
from stress_risk.utils.data import get_all_behavior
#from tms_risk.utils.data import Subject as TMSSubject
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


# %%
df = get_all_behavior(bids_folder='/Users/mrenke/data/ds-stressrisk')
df_cond = pd.read_csv('/Users/mrenke/data/ds-stressrisk/StressRiskNum_ConditionAssigned.csv')

df_c = pd.DataFrame({'subject' : df_cond['SUBID'], 'group': np.asarray(df_cond['condition']).astype(int)})
df_c = df_c[df_c['subject'] < 100] # drop TMS subs


#%% add groups according to df_c to df

gr = []
for i in range(0,len(df)):
    sub = df.index[i][0] #subject is the first (0th) index
    #print(sub)
    group = df_c['group'][df_c['subject'] == sub]
    if len(group) == 1:
        gr.append(int(group))
    else:
        gr.append(np.NaN)

df['group'] = gr    
df
# %%
import bambi

df['x'] = df['log(risky/safe)']
df = df.dropna()
#%%
#fac = sns.lmplot(x='log(risky/safe)', y='chose_risky', data=df.reset_index(), logistic=True, col='subject', hue='risky_first')
fac = sns.lmplot(x='log(risky/safe)', y='chose_risky', data=df.reset_index(), logistic=True, col='group', hue='session')

for ax in fac.axes.ravel():
    ax.axhline(.5, c='k', ls='--')


# %%
# formulae : https://bambinos.github.io/formulae/notebooks/getting_started.html#Adding-interactions
formulae = 'chose_risky ~ x*session + session:group + x:session:group + (x*session|subject)'
model = bambi.Model(formulae, link='probit', family='bernoulli', data=df.reset_index())
#model = bambi.Model('chose_risky ~ x + (x|subject) + (x|(group*session))', link='probit', family='bernoulli', data=df.reset_index())
#model = bambi.Model('chose_risky ~ x + (x:group:session|subject)', link='probit', family='bernoulli', data=df.reset_index())
#model = bambi.Model('chose_risky ~ x + (x|subject)', link='probit', family='bernoulli', data=df.reset_index())

#model.build()

traces = model.fit(init='adapt_diag', target_accept=0.9, draws=1000, tune=1000)
# problem: https://discourse.pymc.io/t/installation-issue-with-aesara/10642
# %%
import arviz as az

az.plot_trace(traces)
# %%
import scipy.stats as ss
def invprobit(x):
    return ss.norm.ppf(x)

def extract_rnp_precision(trace, model, data, group=False):

    data = data.reset_index()

    if group:
        fake_data = pd.MultiIndex.from_product([data.reset_index()['subject'].unique()[[0]],
                                                [0, 1],
                                                data['session'].unique(),
                                                data['group'].unique()],
                                                names=['subject', 'x', 'session', 'group']
                                                ).to_frame().reset_index(drop=True)
    else:
        fake_data = pd.MultiIndex.from_product([data.reset_index()['subject'].unique(),
                                                [0, 1],
                                                data['session'].unique(),
                                                data['group'].unique()],
                                                names=['subject', 'x', 'session', 'group']
                                                ).to_frame().reset_index(drop=True)

    #pred = model.predict(trace, 'mean', fake_data, inplace=False)['posterior']['chose_risky_mean']
    pred = model.predict(trace, 'mean', fake_data, inplace=False, include_group_specific=not group)['posterior']['chose_risky_mean']

    pred = pred.to_dataframe().unstack([0, 1])
    pred = pred.set_index(pd.MultiIndex.from_frame(fake_data))

    # return pred

    pred0 = pred.xs(0, 0, 'x')
    intercept = pd.DataFrame(invprobit(pred0), index=pred0.index, columns=pred0.columns)
    gamma = invprobit(pred.xs(1, 0, 'x')) - intercept

    return intercept, gamma
# %%

intercept, gamma = extract_rnp_precision(traces, model, df, True)

rnp = np.clip(np.exp(intercept/gamma), 0, 1)

rnp = rnp.stack([1,2])
rnp.columns = ['rnp']
#%%
#fac = sns.catplot(x='subject', y='rnp', data=rnp.reset_index(), aspect=5., kind='violin', color='gray')
fac = sns.catplot(x='group', y='rnp', hue='session', data=rnp.reset_index(), aspect=5., kind='violin')

plt.ylim(0, 1)
plt.axhline(.55, c='k', ls='--', label='risk-neutral')
fac.set(title= formulae, ylabel='Risk neutral probability')
fac.add_legend()
#%%
p = rnp.reset_index()

pp = np.asarray(p[(p['session']==2) & (p['group']==1)]['rnp']) -  np.asarray(p[(p['session']==2) & (p['group']==0)]['rnp'])
plt.hist(pp, bins=50)
plt.axvline(0, c='k', ls='--')

np.mean(pp>0)

#%%
g = gamma.stack([1,2])
g.columns  = ['gamma']
g = g.reset_index()

gg= np.asarray(g[(g['session']==2) & (g['group']==1)]['gamma']) -  np.asarray(g[(g['session']==2) & (g['group']==0)]['gamma'])
plt.hist(gg, bins=50)
plt.axvline(0, c='k', ls='--')

plt.axvline(0, c='k', ls='--')
np.mean(gg<0)
# %%
gamma_ = gamma.stack([1, 2]).groupby(['subject']).mean()
gamma_.columns = ['gamma']

rnp_ = rnp.groupby(['subject']).mean()

pars = rnp_.join(gamma_)
sns.lmplot(x='rnp', y='gamma', data=pars)
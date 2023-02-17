

#%%
from stress_risk.behavior.utils import get_data, add_cond2df
import pingouin as pg
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


bids_folder = '/Users/mrenke/data/ds-stressrisk'
data = get_data(bids_folder)

d = pd.DataFrame(data.groupby(['subject','session'])['chose_risky'].mean())
d = add_cond2df(d)

pg.intraclass_corr(data=d.reset_index(), raters='subject', targets='session', ratings='chose_risky')
pg.intraclass_corr(data=d.reset_index(), raters='session', targets='subject', ratings='chose_risky')


dd= d.unstack('session') # dd.columns.levels -->  FrozenList([['chose_risky'], [1, 2]])
df = pd.DataFrame(data = {'ses1' : dd['chose_risky', 1].tolist(),'ses2': dd['chose_risky', 2].tolist(),'group': dd['group', 1].tolist()})
sns.lmplot(df, x='ses1',y='ses2', hue='group')

sns.jointplot(df, x='ses1',y='ses2', hue='group')
# %%
rnp = pd.DataFrame(pd.read_csv('/Users/mrenke/git/stress_risk/stress_risk/behavior/subject-session-wise_rnp.tsv', sep='\t', index_col='subject'))
tmp = data.groupby(['subject', 'group', 'session']).mean()
# combine both dataframes
com = pd.merge(tmp.reset_index(), rnp.reset_index(), how='left', on= ['subject', 'session', 'group'])

dd
d = pd.DataFrame(data = {'ses1' : com[com['session']==1]['rnp'].tolist(),'ses2': com[com['session']==2]['rnp'].tolist(),'group': com[com['session']==1]['group'].tolist()})

g = sns.lmplot(d, x='ses1',y='ses2', hue='group')
g.set(xlim=(0,1))
g.set(title = 'rnp correlation between sessions')
# %% simple correlation
pg.corr(com[(com.session == 1) & (com.group == 0)]['rnp'], com[(com.session == 2) & (com.group == 0)]['rnp'])

pg.corr(com[(com.session == 1) & (com.group == 1)]['rnp'], com[(com.session == 2) & (com.group == 1)]['rnp'])
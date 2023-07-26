import os.path as op
import os
import numpy as np
import pandas as pd
from bauer.models import RiskRegressionModel, ExpectedUtilityRiskRegressionModel
from stress_risk.utils.data import get_all_behavior
import arviz as az
import matplotlib.pyplot as plt
import seaborn as sns



def get_data(bids_folder='/Users/mrenke/data/ds-stressrisk'):
    df = get_all_behavior(bids_folder=bids_folder)
    df['choice'] = df['choice'] == 2.0
    df['p1'] = df['prob1']
    df['p2'] = df['prob2']

    df = add_cond2df(df) # adds 
    df = df.dropna() # automatially removes subs without group assignment
    df = df.reset_index(level= 'session', drop=False) 
    return df

def add_cond2df(df):
    #df_cond = pd.read_csv('/Users/mrenke/data/ds-stressrisk/StressRiskNum_ConditionAssigned.csv')
    df_cond = pd.read_excel('/Users/mrenke/data/ds-stressrisk/addMeasures/data_combined.xlsx')
    df_c = pd.DataFrame({'subject' : df_cond['SUBID'], 'group': np.asarray(df_cond['condition']).astype(int)})
    df_c = df_c[df_c['subject'] < 100] # drop TMS subs
    # df_c.to_csv(op.join('/Users/mrenke/data/ds-stressrisk','sub-grou_assignmentList.csv'))
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

    return df


def build_model(model_label, df):
    if model_label == '1':
        model = RiskRegressionModel(df,regressors={'n1_evidence_sd':'session*group',
         'n2_evidence_sd':'session*group', 'risky_prior_mu':'session*group', 'risky_prior_std':'session*group',
          'safe_prior_mu':'session*group', 'safe_prior_std':'session*group'},
         prior_estimate='full')
    elif model_label == '1_null':
        model = RiskRegressionModel(df, regressors={},
         prior_estimate='full')
    elif model_label == '1a':
        model = RiskRegressionModel(df, regressors={'n1_evidence_sd':'session*group', 'n2_evidence_sd':'session*group',
        'risky_prior_mu':'session*group'},
         prior_estimate='full')
    elif model_label == '2': # only evidence_sd 
        model = RiskRegressionModel(df, regressors={'n1_evidence_sd':'session*group',
         'n2_evidence_sd':'session*group'},
         prior_estimate='full')   
    elif model_label == '3': # only priors
        model = RiskRegressionModel(df, regressors={'risky_prior_mu':'session*group', 'risky_prior_std':'session*group',
          'safe_prior_mu':'session*group', 'safe_prior_std':'session*group'},
         prior_estimate='full')                
    elif model_label == '4':
         model = RiskRegressionModel(df, regressors={'n1_evidence_sd':'session*group',
          'risky_prior_mu':'session*group'},
         prior_estimate='different')
    elif model_label =='EU_1':
        model = ExpectedUtilityRiskRegressionModel(df, save_trialwise_eu= True, regressors=None) #subject is automatically a regressor
    elif model_label =='EU_2':
        model = ExpectedUtilityRiskRegressionModel(df, save_trialwise_eu= True, regressors={'alpha':'0 + C(session)','sigma':'0 + C(session)'}) #subject is automatically a regressor
    elif model_label =='EU_3':
        model = ExpectedUtilityRiskRegressionModel(df, save_trialwise_eu= True, regressors={'alpha':'0 + C(session)*group', 'sigma':'0 + C(session)*group'}) #subject is automatically a regressor
    elif model_label =='NLC_1': # same as '1', just with save_trialwise_n_estimates
        model = RiskRegressionModel(df,save_trialwise_n_estimates=True, regressors={'n1_evidence_sd':'session*group',
         'n2_evidence_sd':'session*group', 'risky_prior_mu':'session*group', 'risky_prior_std':'session*group',
          'safe_prior_mu':'session*group', 'safe_prior_std':'session*group'},
         prior_estimate='full')
    elif model_label=='5' :
        model = RiskRegressionModel(df,regressors={'n1_evidence_sd':'session*group',
         'n2_evidence_sd':'session*group', 'prior_mu':'0 + session*group', 'risky_prior_std':'session*group', # 0 == no intercept for that regressor
        'safe_prior_std':'session*group'},
         prior_estimate='full')
    else:
        raise Exception(f'Do not know model label {model_label}')

    return model


# --- funcs for analysis----------------------------

def summarize_ppc(ppc, groupby=None):

    if groupby is not None:
        ppc = ppc.groupby(groupby).mean()

    e = ppc.mean(1).to_frame('p_predicted')
    hdi = pd.DataFrame(az.hdi(ppc.T.values), index=ppc.index,
                       columns=['hdi025', 'hdi975'])

    return pd.concat((e, hdi), axis=1)

def cluster_offers(d, n=6, key='log(risky/safe)'):
    return pd.qcut(d[key], n, duplicates='drop').apply(lambda x: x.mid)

def plot_prediction(data, x, color, y='p_predicted', alpha=.5, **kwargs):
    data = data[~data['hdi025'].isnull()]

    plt.fill_between(data[x], data['hdi025'],
                     data['hdi975'], color=color, alpha=alpha)
    plt.plot(data[x], data[y], color=color)

def get_rnp(intercept, gamma):
    rnp = np.exp(intercept['intercept']/gamma['gamma'])

    rnp = pd.concat((rnp, ), keys=['rnp'], axis=1)
    return rnp

# main function needed by analyze_bauer_model2.py
def plot_ppc(df, ppc, plot_type=1, var_name='ll_bernoulli', level='subject', col_wrap=5):

    assert (var_name in ['p', 'll_bernoulli'])

    ppc = ppc.xs(var_name, 0, 'variable').copy()

    df = df.copy()

    # Make sure that we group data from (Roughly) same fractions
    if not (df.groupby(['subject', 'log(risky/safe)']).size().groupby('subject').size() < 7).all():
        df['log(risky/safe)'] = df.groupby(['subject'],
                                        group_keys=False).apply(cluster_offers)

    if level == 'group':
        df['log(risky/safe)'] = df['bin(risky/safe)']
        ppc = ppc.reset_index('log(risky/safe)')
        ppc['log(risky/safe)'] = ppc.index.get_level_values('bin(risky/safe)')

    if plot_type == 1:
        groupby = ['risky_first', 'log(risky/safe)']
    elif plot_type in [2, 4]:
        groupby = ['risky_first', 'n_safe']
    elif plot_type in [3, 5]:
        groupby = ['risky_first', 'n_safe', 'log(risky/safe)']
    elif plot_type in [6]:
        groupby = ['risky_first', 'n_safe', 'session','group']
    elif plot_type in [7]:
        groupby = ['risky_first', 'log(risky/safe)', 'session','group']
    elif plot_type in [8, 9]:
        groupby = ['risky_first', 'log(risky/safe)', 'session','group' ,'n_safe']
    elif plot_type in [10, 11]:
        groupby = ['log(risky/safe)', 'session','group']
    else:
        raise NotImplementedError

    if level == 'group':
        ppc = ppc.groupby(['subject']+groupby).mean()

    if level == 'subject':
        groupby = ['subject'] + groupby

    ppc_summary = summarize_ppc(ppc, groupby=groupby)
    p = df.groupby(groupby)[['chose_risky']].mean()
    ppc_summary = ppc_summary.join(p).reset_index()

    if 'risky_first' in groupby:
        ppc_summary['Order'] = ppc_summary['risky_first'].map({True:'Risky first', False:'Safe first'})

    if 'n_safe' in groupby:
        ppc_summary['Safe offer'] = ppc_summary['n_safe'].astype(int)

    ppc_summary['Prop. chosen risky'] = ppc_summary['chose_risky']

    if 'log(risky/safe)' in groupby:
        if level == 'group':
            ppc_summary['Predicted acceptance'] = ppc_summary['log(risky/safe)']
        else:
            ppc_summary['Log-ratio offer'] = ppc_summary['log(risky/safe)']

    if plot_type in [2, 6]:
        x = 'Safe offer'
    else:
        if level == 'group':
            x = 'Predicted acceptance'
        else:
            x = 'Log-ratio offer'



    if plot_type in [1, 2]:
        fac = sns.FacetGrid(ppc_summary,
                            col='subject' if level == 'subject' else None,
                            hue='Order',
                            col_wrap=col_wrap if level == 'subject' else None)

    elif plot_type == 3:
        fac = sns.FacetGrid(ppc_summary,
                            col='Safe offer',
                            hue='Order',
                            row='subject' if level == 'subject' else None)
    elif plot_type == 4:


        if level == 'group':
            rnp = df.groupby(['subject'] + groupby, group_keys=False).apply(get_rnp).to_frame('rnp')
            rnp = rnp.groupby(groupby).mean()
        else:
            rnp = df.groupby(groupby, group_keys=False).apply(get_rnp).to_frame('rnp')

        ppc_summary = ppc_summary.join(rnp)
        fac = sns.FacetGrid(ppc_summary,
                            hue='Order',
                            col='subject' if level == 'subject' else None,
                            col_wrap=col_wrap if level == 'subject' else None)

        fac.map_dataframe(plot_prediction, x='Safe offer', y='p_predicted')
        fac.map(plt.scatter, 'Safe offer', 'rnp')
        fac.map(lambda *args, **kwargs: plt.axhline(.55, c='k', ls='--'))

    elif plot_type == 5:
        fac = sns.FacetGrid(ppc_summary,
                            col='Order',
                            hue='Safe offer',
                            row='subject' if level == 'subject' else None,
                            palette='coolwarm')

    elif plot_type == 6:
        fac = sns.FacetGrid(ppc_summary,
                            col='Order',
                            hue='session',
                            row='subject' if level == 'subject' else 'group',
                            palette=sns.color_palette()[2:])

    elif plot_type == 7:
        fac = sns.FacetGrid(ppc_summary,
                            col='Order',
                            hue='session',
                            row='subject' if level == 'subject' else 'group',
                            palette=sns.color_palette()[2:])

    elif plot_type == 8:
        if level == 'subject':
            raise NotImplementedError

        fac = sns.FacetGrid(ppc_summary,
                            col='Order',
                            hue='Safe offer',
                            row='session', ##
                            palette='coolwarm')

    elif plot_type == 9:
        if level == 'subject':
            raise NotImplementedError

        fac = sns.FacetGrid(ppc_summary,
                            col='Order',
                            hue='session',##
                            row='Safe offer',
                            palette=sns.color_palette()[2:]
                            )

    elif plot_type == 10:
        fac = sns.FacetGrid(ppc_summary,
                            hue='session',
                            col='group',
                            palette=sns.color_palette()[2:])
        
    elif plot_type == 11:
        fac = sns.FacetGrid(ppc_summary,
                            hue='group',
                            col='session',
                            palette=sns.color_palette()[4:])        
        

    if plot_type in [1,2,3, 5, 6, 7, 8, 9, 10, 11]:
        fac.map_dataframe(plot_prediction, x=x)
        fac.map(plt.scatter, x, 'Prop. chosen risky')
        fac.map(lambda *args, **kwargs: plt.axhline(.5, c='k', ls='--'))

    if plot_type in [1, 3, 5, 7, 9, 10, 11]:
        if level == 'subject':
            fac.map(lambda *args, **kwargs: plt.axvline(np.log(1./.55), c='k', ls='--'))
        else:
            fac.map(lambda *args, **kwargs: plt.axvline(2.5, c='k', ls='--'))

    
    fac.add_legend()

    return fac    

def format_bambi_ppc(trace, model, df):

    preds = []
    for key, kind in zip(['ll_bernoulli', 'p'], ['pps', 'mean']):
        pred = model.predict(trace, kind=kind, inplace=False) 
        if kind == 'pps':
            pred = pred['posterior_predictive']['chose_risky'].to_dataframe().unstack(['chain', 'draw'])['chose_risky']
        else:
            pred = pred['posterior']['chose_risky_mean'].to_dataframe().unstack(['chain', 'draw'])['chose_risky_mean']
        pred.index = df.index
        pred = pred.set_index(pd.MultiIndex.from_frame(df), append=True)
        preds.append(pred)

    pred = pd.concat(preds, keys=['ll_bernoulli', 'p'], names=['variable'])
    return pred

import scipy.stats as ss
def invprobit(x):
    return ss.norm.ppf(x)


def extract_rnp_precision(trace, model, data, group=False):

    data = data.reset_index()

    if group:
        fake_data = pd.MultiIndex.from_product([data.reset_index()['subject'].unique()[[0]], # use just one subject
                                                [0, 1],
                                                data['session'].unique(),
                                                data['group'].unique(),
                                                data['risky_first'].unique(),
                                                data['n_safe'].unique()],
                                                names=['subject', 'x', 'session', 'group', 'risky_first', 'n_safe']
                                                ).to_frame().reset_index(drop=True)
    else:
        fake_data = pd.MultiIndex.from_product([data.reset_index()['subject'].unique(),
                                                [0, 1],
                                                data['session'].unique(),
                                                data['group'].unique(),
                                                data['risky_first'].unique(),
                                                data['n_safe'].unique()],
                                                names=['subject', 'x', 'session', 'group', 'risky_first', 'n_safe']).to_frame().reset_index(drop=True)


    #pred = model.predict(trace, 'mean', fake_data, inplace=False)['posterior']['chose_risky_mean']
    pred = model.predict(trace, 'mean', fake_data, inplace=False, include_group_specific=not group)['posterior']['chose_risky_mean']

    pred = pred.to_dataframe().unstack([0, 1])
    pred = pred.set_index(pd.MultiIndex.from_frame(fake_data))

    # return pred

    pred0 = pred.xs(0, 0, 'x')
    intercept = pd.DataFrame(invprobit(pred0), index=pred0.index, columns=pred0.columns)
    gamma = invprobit(pred.xs(1, 0, 'x')) - intercept

    return intercept, gamma
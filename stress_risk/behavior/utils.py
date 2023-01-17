import os.path as op
import os
import numpy as np
import pandas as pd
from bauer.models import RiskRegressionModel
from stress_risk.utils.data import get_all_behavior



def get_data(bids_folder='/Users/mrenke/data/ds-stressrisk'):
    df = get_all_behavior(bids_folder=bids_folder)
    df['choice'] = df['choice'] == 2.0
    df['p1'] = df['prob1']
    df['p2'] = df['prob2']

    df = add_cond2df(df) # adds 
    df = df.dropna() # automatially removes subs without group assignment
    df = df.reset_index(level= 'session') 
    return df

def add_cond2df(df):
    #df_cond = pd.read_csv('/Users/mrenke/data/ds-stressrisk/StressRiskNum_ConditionAssigned.csv')
    df_cond = pd.read_excel('/Users/mrenke/data/ds-stressrisk/addMeasures/data_combined.xlsx')
    df_c = pd.DataFrame({'subject' : df_cond['SUBID'], 'group': np.asarray(df_cond['condition']).astype(int)})
    df_c = df_c[df_c['subject'] < 100] # drop TMS subs
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
        model = RiskRegressionModel(df, regressors={'n1_evidence_sd':'session*group',
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
    elif model_label == '2':
        model = RiskRegressionModel(df, regressors={'n1_evidence_sd':'session*group',
         'n2_evidence_sd':'session*group', 'risky_prior_mu':'session*group', 'risky_prior_std':'session*group'},
         prior_estimate='different')
    elif model_label == '2a':
        model = RiskRegressionModel(df, regressors={'n2_evidence_sd':'session*group', 'risky_prior_mu':'session*group'},
         prior_estimate='different')
    elif model_label == '2_null':
        model = RiskRegressionModel(df, regressors={},
         prior_estimate='different')
    elif model_label == '3':
        model = RiskRegressionModel(df, regressors={'n1_evidence_sd':'session*group',
         'n2_evidence_sd':'session*group', 'prior_mu':'session*group', 'prior_std':'session*group'},
         prior_estimate='shared')
    elif model_label == '3_null':
        model = RiskRegressionModel(df, regressors={},
         prior_estimate='different')
    elif model_label == '4':
         model = RiskRegressionModel(df, regressors={'n1_evidence_sd':'session*group',
          'risky_prior_mu':'session*group'},
         prior_estimate='different')
    else:
        raise Exception(f'Do not know model label {model_label}')

    return model
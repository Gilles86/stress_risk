from itertools import product
import numpy as np
import pandas as pd
from scipy.stats import norm



def get_subwise_params(idata, param_name):
    df_param= idata.posterior[param_name].to_dataframe()    
    df_param.columns.name = 'parameter'
    df_param.index = df_param.index.set_names(['chain','draw','subject','regressor']) 
    df_param = df_param.stack().to_frame('value')

    df_param = df_param.xs('Intercept', 0,'regressor')
    df_param = df_param.groupby(['subject'])[['value']].mean()
    df_param = df_param.rename(mapper={'value':param_name},axis=1)

    return df_param

def get_posterior(mu1, sd1, mu2, sd2):

    var1, var2 = sd1**2, sd2**2

    return mu1 + (var1/(var1+var2))*(mu2 - mu1), np.sqrt((var1*var2)/(var1+var2))

def get_diff_dist(mu1, sd1, mu2, sd2):
    return mu2 - mu1, np.sqrt(sd1**2+sd2**2)



def simulate_choices_subind_p_var(trials_df, sub_param,p_risky):
    
    n1_prior_mu = np.mean(np.log(trials_df['n1']))
    n1_prior_sd = np.std(np.log(trials_df['n1']))

    n2_prior_sd = np.std(np.log(trials_df['n2']))

    choices = []
    for i in range(0,len(trials_df)):
        r = trials_df.iloc[i]

        n1_evidence_mu = np.log(r['n1'])
        n2_evidence_mu = np.log(r['n2'])
       
        n1_evidence_sd = sub_param.loc[r['subject'],'n1_evidence_sd']
        n2_evidence_sd = sub_param.loc[r['subject'],'n2_evidence_sd']

        n2_prior_mu = sub_param.loc[r['subject'],'n2_prior_mu']

        if trials_df['p1'] == 1: # safe first
            n1_prior_mu, n1_prior_sd = sub_param.loc[r['subject'],'safe_prior_mu'], sub_param.loc[r['subject'],'safe_prior_sd']
            n2_prior_mu, n2_prior_sd = sub_param.loc[r['subject'],'risky_prior_mu'], sub_param.loc[r['subject'],'risky_prior_sd']
        else: # risky first
            n1_prior_mu, n1_prior_sd = sub_param.loc[r['subject'],'risky_prior_mu'], sub_param.loc[r['subject'],'risky_prior_sd']
            n2_prior_mu, n2_prior_sd = sub_param.loc[r['subject'],'safe_prior_mu'], sub_param.loc[r['subject'],'safe_prior_sd']


        post_n1_mu, post_n1_sd = get_posterior(n1_prior_mu, 
                                                n1_prior_sd, 
                                                n1_evidence_mu, 
                                                n1_evidence_sd
                                                )

        post_n2_mu, post_n2_sd = get_posterior(n2_prior_mu,
                                                n2_prior_sd,
                                                n2_evidence_mu, 
                                                n2_evidence_sd)

        diff_mu, diff_sd = get_diff_dist( post_n1_mu, post_n1_sd, post_n2_mu, post_n2_sd)

        ['threshold'] =  np.log(trials_df['p2'] / trials_df['p1'])
        p = norm.cdf(diff_mu, scale = diff_sd)
        choice = int(np.random.binomial(1, p, 1)) # 
        
        choices.append(choice)

    trials_df['sim_choice'] = choices

    return trials_df

# or do it not with n2_chosen but risky_chosen

def simulate_choices_subind_p_var(trials_df, sub_param,p_risky):
    
    n1_prior_mu = np.mean(np.log(trials_df['n1']))
    n1_prior_sd = np.std(np.log(trials_df['n1']))

    n2_prior_sd = np.std(np.log(trials_df['n2']))

    choices = []
    for i in range(0,len(trials_df)):
        r = trials_df.iloc[i]

        n1_evidence_mu = np.log(r['n1'])
        n2_evidence_mu = np.log(r['n2'])
       
        n1_evidence_sd = sub_param.loc[r['subject'],'n1_evidence_sd']
        n2_evidence_sd = sub_param.loc[r['subject'],'n2_evidence_sd']

        n2_prior_mu = sub_param.loc[r['subject'],'n2_prior_mu']

        if trials_df['p1'] == 1: # safe first
            n1_prior_mu, n1_prior_sd = sub_param.loc[r['subject'],'safe_prior_mu'], sub_param.loc[r['subject'],'safe_prior_sd']
            n2_prior_mu, n2_prior_sd = sub_param.loc[r['subject'],'risky_prior_mu'], sub_param.loc[r['subject'],'risky_prior_sd']
        else: # risky first
            n1_prior_mu, n1_prior_sd = sub_param.loc[r['subject'],'risky_prior_mu'], sub_param.loc[r['subject'],'risky_prior_sd']
            n2_prior_mu, n2_prior_sd = sub_param.loc[r['subject'],'safe_prior_mu'], sub_param.loc[r['subject'],'safe_prior_sd']


        post_n1_mu, post_n1_sd = get_posterior(n1_prior_mu, 
                                                n1_prior_sd, 
                                                n1_evidence_mu, 
                                                n1_evidence_sd
                                                )

        post_n2_mu, post_n2_sd = get_posterior(n2_prior_mu,
                                                n2_prior_sd,
                                                n2_evidence_mu, 
                                                n2_evidence_sd)

        diff_mu, diff_sd = get_diff_dist( post_n1_mu, post_n1_sd, post_n2_mu, post_n2_sd)

        ['threshold'] =  np.log(trials_df['p2'] / trials_df['p1'])
        p = norm.cdf(diff_mu, scale = diff_sd)
        choice = int(np.random.binomial(1, p, 1)) # 
        
        choices.append(choice)

    trials_df['sim_choice'] = choices

    return trials_df
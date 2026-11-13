import argparse
from bauer.models import RiskRegressionModel
#from tms_risk.utils.data import get_all_behavior
from stress_risk.utils.data import get_all_behavior
import os.path as op
import os
import arviz as az
import numpy as np
import pandas as pd
from utils import add_cond2df, build_model, get_data

# for value estimates for GLM - if save_trialwise=True - script for extracting pEV in fmri/glm_scripts/create_evenstFIles.ipynb

def main(model_label, burnin=1000, samples=1000, bids_folder = '/Users/mrenke/data/ds-stressrisk',AUC=False,E_dif=False):

    target_folder = op.join(bids_folder, 'derivatives', 'cogmodels')
    
    if not op.exists(target_folder):
        os.makedirs(target_folder)

    df = get_data(bids_folder)
    
    df_comb_shifts = pd.read_csv('/Users/mrenke/data/ds-stressrisk/interim_sum_data/r-prior-shift_Ediff_AUC.csv')
    df = df.join(df_comb_shifts.set_index('subject')[['AUC', 'E_dif']], on='subject', how='left')
    
    if AUC:
        df.dropna(subset=['AUC'], inplace=True) # remove subjects without AUC
    if E_dif:
        df.dropna(subset=['E_dif'], inplace=True) # remove subjects without E_dif

    if model_label in ['0', '5']:
        target_accept = 0.9
    elif model_label == 'NLC_1':
        target_accept = 0.85
    else:
        target_accept = 0.9

    model = build_model(model_label, df)
    model.build_estimation_model()
    trace = model.sample(burnin, samples, target_accept=target_accept)
    az.to_netcdf(trace,
                    op.join(target_folder, f'model-{model_label}_trace.netcdf'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model_label', default=None)
    parser.add_argument('--bids_folder', default='/Users/mrenke/data/ds-stressrisk')
    parser.add_argument('--AUC', action='store_true')
    parser.add_argument('--E_dif', action='store_true')

    args = parser.parse_args()

    main(args.model_label, bids_folder=args.bids_folder, AUC=args.AUC, E_dif=args.E_dif)


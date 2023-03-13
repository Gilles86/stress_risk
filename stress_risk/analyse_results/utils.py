import pandas as pd
import os.path as op
import numpy as np
from stress_risk.utils.data import get_all_behavior
from tqdm.contrib.itertools import product
import matplotlib.pyplot as plt
#import pingouin
import seaborn as sns

# E['sd'] = np.trapz(np.abs(E.values - pdf.columns.astype(float).values[np.newaxis, :]) * pdf, pdf.columns, axis=1)

def get_decoding_info(subject, session,  bids_folder='/data/ds-stressrisk', mask='NPC_R', n_voxels=250):

    subject = f'{subject:02d}'
    key = 'decoded_pdfs.volume.denoise'

    pdf = op.join(bids_folder, 'derivatives', key, f'sub-{subject}', 'func', f'sub-{subject}_ses-{session}_mask-{mask}_nvoxels-{n_voxels}_space-T1w_pars.tsv')

    if op.exists(pdf):
        pdf = pd.read_csv(pdf, sep='\t', index_col=[0])
        pdf.columns = pdf.columns.astype(float)

        E = (pdf*pdf.columns.values[np.newaxis, :] / pdf.sum(1).values[:, np.newaxis]).sum(1)

        E = pd.concat((E,), keys=[(int(subject), int(session), mask, n_voxels)],
        names=['subject', 'session', 'mask', 'n_voxels']).to_frame('E')

        pdf /= np.trapz(pdf, pdf.columns.astype(float))[:, np.newaxis] #normalizing

        E['sd'] = np.trapz(np.abs(E.values - pdf.columns.astype(float).values[np.newaxis, :]) * pdf, pdf.columns, axis=1)
        #print('succesfully predicted')

        return E
    else:
        print(pdf)
        return pd.DataFrame(np.zeros((0, 0)))
    

def get_data(bids_folder='/Users/mrenke/data/ds-stressrisk'):
    df = get_all_behavior(bids_folder=bids_folder)
    df['choice'] = df['choice'] == 2.0
    df['p1'] = df['prob1']
    df['p2'] = df['prob2']

    df = add_cond2df(df) # adds 
    df = df.dropna() # automatially removes subs without group assignment
    df = df.reset_index(level= 'session', drop=False) 
    return df
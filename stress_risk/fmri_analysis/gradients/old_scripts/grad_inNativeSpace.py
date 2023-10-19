#%%
from nilearn.connectome import ConnectivityMeasure
from brainspace.gradient import GradientMaps
from brainspace.utils.parcellation import map_to_labels
import numpy as np
import nibabel as nib
from nilearn import datasets
import os.path as op
import os
from nilearn import signal
import pandas as pd
from scipy.sparse.csgraph import connected_components

import numpy as np
import nibabel as nib
import os.path as op
import pandas as pd
from nilearn import signal
from nilearn import datasets

#from utils import cleanTS

bids_folder = '/Users/mrenke/data/ds-stressrisk'

bids_folder = '/Volumes/mrenkeED/data/ds-stressrisk'
sub = '01' 
ses = 1
runs = range(1, 7)

specification = 'pureNativeSpace'

# %%
def cleanTS(sub, ses, runs = range(1, 7),space = 'fsaverage5', bids_folder='/Users/mrenke/data/ds-stressrisk'):
    # load in data as timeseries and regress out confounds (for each run sepeprately)
    number_of_vertex = 20484  # 'fsaverage5', 10242 * 2

    fmriprep_confounds_include = ['global_signal', 'dvars', 'framewise_displacement', 'trans_x',
                                    'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z',
                                    'a_comp_cor_00', 'a_comp_cor_01', 'a_comp_cor_02', 'a_comp_cor_03', 'cosine00', 'cosine01', 'cosine02'
                                    ] # 

    clean_ts_runs = []

    for run in runs:
        timeseries = [None] * 2
        for i, hemi in enumerate(['L', 'R']):
            filename = op.join(bids_folder,'derivatives', 'fmriprep', f'sub-{sub}', f'ses-{ses}', 'func', 
            f'sub-{sub}_ses-{ses}_task-risk_run-{run}_space-{space}_hemi-{hemi}_bold.func.gii')
            timeseries[i] = nib.load(filename).agg_data()
        timeseries = np.vstack(timeseries) # (20484, 135)

        fmriprep_confounds_file = op.join(bids_folder,'derivatives', 'fmriprep', f'sub-{sub}', f'ses-{ses}', 'func', f'sub-{sub}_ses-{ses}_task-risk_run-{run}_desc-confounds_timeseries.tsv')
        fmriprep_confounds = pd.read_table(fmriprep_confounds_file)[fmriprep_confounds_include] 
        fmriprep_confounds= fmriprep_confounds.fillna(method='bfill')

        #clean_ts_list[run] = signal.clean(timeseries.T, confounds=fmriprep_confounds).T
        clean_ts = signal.clean(timeseries.T, confounds=fmriprep_confounds).T

        clean_ts_runs.append(pd.DataFrame(clean_ts))

    clean_ts_runs = pd.concat(clean_ts_runs, axis=1)
    clean_ts_runs = clean_ts_runs.to_numpy()

    return clean_ts_runs
# %%

clean_ts = cleanTS(sub, ses, runs = runs,space = 'fsnative')
#clean_ts = cleanTS(sub, ses, runs = runs,space = 'fsaverage5', bids_folder=bids_folder)

seed_ts = clean_ts#[mask]
correlation_measure = ConnectivityMeasure(kind='correlation')

# filter out nodes that are not connected to the rest
graph = correlation_measure.fit_transform([seed_ts.T])[0] #correlation_matrix_noParcel
print('raw connectivity matrix estimated')

cc = connected_components(graph)
mask_cc = cc[1] == 0 # all nodes in 0 belong to the largest connected component, check #-components in cc[0]
#mask[mask == True] = mask_cc # mark nodes not in component 0  as False in mask
print('mask with connected components created')

seed_ts_fil = clean_ts[mask_cc]

#now perform embedding on cleaned data
correlation_measure = ConnectivityMeasure(kind='correlation')
correlation_matrix = correlation_measure.fit_transform([seed_ts_fil.T])[0]
gm = GradientMaps(n_components=2, random_state=0)
gm.fit(correlation_matrix_noParcel)

grad_noParcel = [None] * 2
for i, g in enumerate(gm_noParcel.gradients_.T):
    grad_noParcel[i] = map_to_labels(g, labeling_noParcel, mask=mask, fill=np.nan)

print('gradients generated')

saveGradToNPFile(grad_noParcel, sub,ses, specification, bids_folder=bids_folder)

# %%
print('x')
# %%

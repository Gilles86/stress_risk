#%%
import os.path as op
from nilearn.glm.first_level import make_first_level_design_matrix
from nilearn import surface, image
from nilearn.maskers import NiftiMasker
import nibabel as nb
import pandas as pd
import numpy as np
from nibabel import gifti
from tqdm import tqdm
from tqdm.contrib.itertools import product
from sklearn.decomposition import PCA

import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

#%%
def get_volume_mask(subject, session, mask, bids_folder='/data', task_name = 'risk'):

    # if session.endswith('1'):   task  = 'mapper'; else:  task  = 'task'

    base_mask = op.join(bids_folder, 'derivatives', f'fmriprep/sub-{subject}/ses-{session}/func/sub-{subject}_ses-{session}_task-{task_name}_run-1_space-T1w_desc-brain_mask.nii.gz')

    if mask is None:
        return base_mask

    #mask = mask.replace('_', '')
    #mask = op.join(bids_folder, 'derivatives', 'ips_masks', f'sub-{subject}', f'sub-{subject}_space-T1w_desc-{mask}_mask.nii.gz')
    mask = op.join(bids_folder, 'derivatives', 'ips_masks', f'sub-{subject}',f'sub-{subject}_space-T1w_desc-{mask}.nii.gz')
    mask = image.resample_to_img(mask, base_mask, interpolation='nearest')

    return mask

#%%
def get_single_trial_volume(subject, session, mask=None, bids_folder='/data',
        smoothed=False,
        pca_confounds=False,
        task_name = 'risk'
        ):

    key= 'glm_stim1'

    if smoothed:
        key += '.smoothed'

    if pca_confounds:
        key += '.pca_confounds'

    fn = op.join(bids_folder, 'derivatives', key, f'sub-{subject}', f'ses-{session}', 'func', 
            f'sub-{subject}_ses-{session}_task-{task_name}_space-T1w_desc-stims1_pe.nii.gz')

    im = image.load_img(fn)
    
    mask = get_volume_mask(subject, session, mask, bids_folder, task_name)
    # paradigm = get_task_behavior(subject, session, bids_folder)
    masker = NiftiMasker(mask_img=mask)

    data = pd.DataFrame(masker.fit_transform(im))

    return data

#%%
def get_prf_parameters_volume(subject, session, bids_folder,
        run=None,
        smoothed=False,
        pca_confounds=False,
        cross_validated=True,
        hemi=None,
        mask=None,
        space='fsnative'):

    dir = 'encoding_model'
    if cross_validated:
        if run is None:
            raise Exception('Give run')

        dir += '.cv'

    if smoothed:
        dir += '.smoothed'

    if pca_confounds:
        dir += '.pca_confounds'

    parameters = []

    keys = ['mu', 'sd', 'amplitude', 'baseline']

    mask = get_volume_mask(subject, session, mask, bids_folder)
    masker = NiftiMasker(mask)

    for parameter_key in keys:
        if cross_validated:
            fn = op.join(bids_folder, 'derivatives', dir, f'sub-{subject}', f'ses-{session}', 
                    'func', f'sub-{subject}_ses-{session}_run-{run}_desc-{parameter_key}.optim_space-T1w_pars.nii.gz')
        else:
            fn = op.join(bids_folder, 'derivatives', dir, f'sub-{subject}', f'ses-{session}', 
                    'func', f'sub-{subject}_ses-{session}_desc-{parameter_key}.optim_space-T1w_pars.nii.gz')
        
        pars = pd.Series(masker.fit_transform(fn).ravel())
        parameters.append(pars)

    return pd.concat(parameters, axis=1, keys=keys, names=['parameter'])

#%%
def get_surf_mask(subject, mask, hemi=None, bids_folder='/data'):

    if hemi is None:
        mask_l = get_surf_mask(subject, mask, 'L', bids_folder )
        mask_r = get_surf_mask(subject, mask, 'R', bids_folder )
        return pd.concat((mask_l, mask_r), axis=1, keys=['L', 'R'], names=['hemi'])
        

    fs_hemi = {'L':'lh', 'R':'rh'}[hemi]

    fs_subject = f'sub-{subject}'
    fn = op.join(bids_folder, 'derivatives', 'freesurfer', 
            get_fs_subject(subject), 'surf',
            f'{fs_hemi}.{mask}.mgz')

    d = surface.load_surf_data(fn).astype(np.bool)
    d = pd.Series(d, index=pd.Index(np.arange(len(d)), name='vertex'))
    return d

#%%

class Subject(object):

    def __init__(self, subject, bids_folder='/data'):

        self.subject = '%02d' % int(subject)
        self.bids_folder = bids_folder

    def get_volume_mask(self, roi='NPC12r'):

        if roi.startswith('NPC'):
            return op.join(self.derivatives_dir
            ,'ips_masks',
            f'sub-{self.subject}',
            'anat',
            f'sub-{self.subject}_space-T1w_desc-{roi}_mask.nii.gz'
            )

        else:
            raise NotImplementedError

    @property
    def derivatives_dir(self):
        return op.join(self.bids_folder, 'derivatives')

    @property
    def fmriprep_dir(self):
        return op.join(self.derivatives_dir, 'fmriprep', f'sub-{self.subject}')

    @property
    def t1w(self):
        t1w = op.join(self.fmriprep_dir,
        'anat',
        'sub-{self.subject}_desc-preproc_T1w.nii.gz')

        if not op.exists(t1w):
            raise Exception(f'T1w can not be found for subject {self.subject}')

        return t1w

    def get_nprf_pars(self, session=1, model='encoding_model.smoothed', parameter='r2',
    volume=True):

        if not volume:
            raise NotImplementedError

        im = op.join(self.derivatives_dir, model, f'sub-{self.subject}',
        f'ses-{session}', 'func', 
        f'sub-{self.subject}_ses-{session}_desc-{parameter}.optim_space-T1w_pars.nii.gz')

        return im

    def get_behavior(self, drop_no_responses=True, sessions=None, task_name = 'risk', N_runs=6):

        if sessions is None:
            sessions = ['3t2', '7t2']

        if type(sessions) is not list:
            sessions = [sessions]

        df = []
        for session in sessions:

            runs = range(1, N_runs+1)
            for run in runs:

                fn = op.join(self.bids_folder, f'sub-{self.subject}/ses-{session}/func/sub-{self.subject}_ses-{session}_task-{task_name}_run-{run}_events.tsv')

                if op.exists(fn):
                    d = pd.read_csv(fn, sep='\t',
                                index_col=['trial_nr', 'trial_type'])
                    d['subject'], d['session'], d['run'] = int(self.subject), session, run
                    df.append(d)

        if len(df) > 0:
            df = pd.concat(df)
            df = df.reset_index().set_index(['subject', 'session', 'run', 'trial_nr', 'trial_type']) 
            df = df.unstack('trial_type')
            
            return self._cleanup_behavior(df, drop_no_responses=drop_no_responses)


        else:
            return pd.DataFrame([])

    @staticmethod
    def _cleanup_behavior(df_, drop_no_responses=True):
        df = df_[[]].copy()
        df['rt'] = df_.loc[:, ('onset', 'choice')] - df_.loc[:, ('onset', 'stimulus 2')]
        df['certainty'] = df_.loc[:, ('choice', 'certainty')]
        df['n1'], df['n2'] = df_['n1']['stimulus 1'], df_['n2']['stimulus 1']
        df['prob1'], df['prob2'] = df_['prob1']['stimulus 1'], df_['prob2']['stimulus 1']

        df['choice'] = df_[('choice', 'choice')]
        df['risky_first'] = df['prob1'] == 0.55
        df['chose_risky'] = (df['risky_first'] & (df['choice'] == 1.0)) | (~df['risky_first'] & (df['choice'] == 2.0))
        df.loc[df.choice.isnull(), 'chose_risky'] = np.nan


        df['n_risky'] = df['n1'].where(df['risky_first'], df['n2'])
        df['n_safe'] = df['n2'].where(df['risky_first'], df['n1'])
        df['frac'] = df['n_risky'] / df['n_safe']
        df['log(risky/safe)'] = np.log(df['frac'])

        def get_risk_bin(d):
            try: 
                return pd.qcut(d, 6, range(1, 7))
            except Exception as e:
                n = len(d)
                ix = np.linspace(1, 7, n, False)

                d[d.sort_values().index] = np.floor(ix)
                
                return d
        df['bin(risky/safe)'] = df.groupby(['subject'])['frac'].apply(get_risk_bin)

        df['chose_risky'] = df['chose_risky'].astype(bool)

        if drop_no_responses:
            df = df[~df.chose_risky.isnull()]

        return df.droplevel(-1, 1)
        

# %%

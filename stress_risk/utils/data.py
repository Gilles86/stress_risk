import os
import os.path as op
from re import I
import pandas as pd
from itertools import product
import numpy as np
import pkg_resources
import yaml
from sklearn.decomposition import PCA
from nilearn import image
from nilearn.maskers import NiftiMasker
from collections.abc import Iterable
from nilearn import surface

def get_data(bids_folder='/Users/mrenke/data/ds-stressrisk',value=False ):
    df = get_all_behavior(bids_folder=bids_folder,value=value )
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


def get_subjects(bids_folder='/data/ds-stressrisk', correct_behavior=True, correct_npc=False):
    subjects = list(range(1, 200))

    subjects = [Subject(subject, bids_folder) for subject in subjects]

    return subjects

def get_all_behavior(bids_folder='/data/ds-stressrisk', correct_behavior=True, correct_npc=False, drop_no_responses=True,value=False ):

    subjects = get_subjects(bids_folder, correct_behavior, correct_npc)
    behavior = [s.get_behavior(drop_no_responses=drop_no_responses, value=value) for s in subjects]
    return pd.concat(behavior)


class Subject(object):

    def __init__(self, subject, bids_folder='/data/ds-stressrisk'):

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
            t1w = op.join(self.fmriprep_dir,
            'ses-1', 'anat',
            f'sub-{self.subject}_ses-1_desc-preproc_T1w.nii.gz')
        
        if not op.exists(t1w):
            raise Exception(f'T1w can not be found for subject {self.subject}')

        return t1w

    def get_preprocessed_bold(self, session=1, runs=None, space='T1w'):
        if runs is None:
            runs = range(1, 7)

        images = [op.join(self.bids_folder, 'derivatives', 'fmriprep', f'sub-{self.subject}',
         f'ses-{session}', 'func', f'sub-{self.subject}_ses-{session}_task-risk_run-{run}_space-{space}_desc-preproc_bold.nii.gz') for run in runs]

        return images

    def get_nprf_pars(self, session=1, model='encoding_model.smoothed', parameter='r2',
    volume=True):

        if not volume:
            raise NotImplementedError

        im = op.join(self.derivatives_dir, model, f'sub-{self.subject}',
        f'ses-{session}', 'func', 
        f'sub-{self.subject}_ses-{session}_desc-{parameter}.optim_space-T1w_pars.nii.gz')

        return im

    def get_behavior(self, sessions=None, drop_no_responses=True,value=False ):
        if sessions is None:
            sessions = [1, 2]

        if not isinstance(sessions, Iterable):
            sessions = [sessions]
        
        value_n = 'value_' if value else ''

        runs = range(1, 7)
        df = []
        for session, run in product(sessions, runs):

            fn = op.join(self.bids_folder, f'sub-{self.subject}/ses-{session}/func/sub-{self.subject}_ses-{session}_task-risk_run-{run}_{value_n}events.tsv')

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

        df['log(n1)'] = np.log(df['n1'])

        if drop_no_responses:
            df = df[~df.chose_risky.isnull()]
            df['chose_risky'] = df['chose_risky'].astype(bool)

        def get_risk_bin(d):
            labels = [f'{int(e)}%' for e in np.linspace(20, 80, 6)]
            try: 
                # return pd.qcut(d, 6, range(1, 7))
                return pd.qcut(d, 6, labels=labels)
            except Exception as e:
                n = len(d)
                ix = np.linspace(0, 6, n, False)

                d[d.sort_values().index] = [labels[e] for e in np.floor(ix).astype(int)]
                
                return d
        df['bin(risky/safe)'] = df.groupby(['subject'], group_keys=False)['frac'].apply(get_risk_bin)

        return df.droplevel(-1, 1)

    def get_fmriprep_confounds(self, session, include=None):

        if include is None:
            include = ['global_signal', 'dvars', 'framewise_displacement', 'trans_x',
                                        'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z',
                                        'a_comp_cor_00', 'a_comp_cor_01', 'a_comp_cor_02', 'a_comp_cor_03', 'cosine00', 'cosine01', 'cosine02', 
                                        'non_steady_state_outlier00', 'non_steady_state_outlier01', 'non_steady_state_outlier02']


        runs = range(1, 7)

        fmriprep_confounds = [
            op.join(self.bids_folder, 'derivatives', 'fmriprep', f'sub-{self.subject}/ses-{session}/func/sub-{self.subject}_ses-{session}_task-risk_run-{run}_desc-confounds_timeseries.tsv') for run in runs]
        fmriprep_confounds = [pd.read_table(
            cf)[include] for cf in fmriprep_confounds]

        return fmriprep_confounds

    def get_retroicor_confounds(self, session, n_cardiac=3, n_respiratory=4, n_interaction=2):

        runs = range(1, 7)

        columns = []
        for n, modality in zip([3, 4, 2], ['cardiac', 'respiratory', 'interaction']):
            for order in range(1, n+1):
                columns += [(modality, order, 'sin'), (modality, order, 'cos')]
        columns = pd.MultiIndex.from_tuples(
            columns, names=['modality', 'order', 'type'])                        

        retroicor_confounds = [
            op.join(self.bids_folder, f'derivatives/physiotoolbox/sub-{self.subject}/ses-{session}/func/sub-{self.subject}_ses-{session}_task-risk_run-{run}_desc-retroicor_timeseries.tsv') for run in runs]
        retroicor_confounds = [pd.read_table(
            cf, header=None, usecols=np.arange(18), names=columns) if op.exists(cf) else pd.DataFrame(np.zeros((135, 0))) for cf in retroicor_confounds]

        retroicor_confounds = pd.concat(retroicor_confounds, 0, keys=runs,
                            names=['run']).sort_index(axis=1)

        retroicor_confounds = pd.concat((retroicor_confounds.loc[:, ('cardiac', slice(n_cardiac))],
                            retroicor_confounds.loc[:, ('respiratory',
                                                slice(n_respiratory))],
                            retroicor_confounds .loc[:, ('interaction', slice(n_interaction))]), axis=1)

        retroicor_confounds = [cf.droplevel('run') for _, cf in retroicor_confounds.groupby(['run'])]


        for cf in retroicor_confounds:
            cf.columns = [f'retroicor_{i}' for i in range(cf.shape[1])]

        return retroicor_confounds 

    def get_confounds(self, session, include_fmriprep=None, include_retroicor=None, pca=False, pca_n_components=.95):
        
        fmriprep_confounds = self.get_fmriprep_confounds(session, include=include_fmriprep)
        retroicor_confounds = self.get_retroicor_confounds(session)
        print(retroicor_confounds)
        confounds = [pd.concat((rcf, fcf), axis=1) for rcf, fcf in zip(retroicor_confounds, fmriprep_confounds)]
        confounds = [c.fillna(method='bfill') for c in confounds]

        if pca:
            def map_cf(cf, n_components=pca_n_components):
                pca = PCA(n_components=n_components)
                cf -= cf.mean(0)
                cf /= cf.std(0)
                cf = pd.DataFrame(pca.fit_transform(cf))
                cf.columns = [f'pca_{i}' for i in range(1, cf.shape[1]+1)]
                return cf
            confounds = [map_cf(cf) for cf in confounds]

        else:
            # remove column names
            confounds = [cf.T.reset_index(drop=True).T for cf in confounds]

        return confounds

    def get_single_trial_volume(self, session, roi=None, 
            denoise=False,
            smoothed=False,
            pca_confounds=False,
            retroicor=False,
            value=False):

        key= 'glm_stim1'

        if denoise:
            key += '.denoise'
        if value:
            key += '.value'

        if pca_confounds:
            key += '.pca_confounds'

        if (retroicor) and (not denoise):
            raise Exception("When not using GLMSingle RETROICOR is *always* used!")

        if retroicor:
            key += '.retroicor'

        if smoothed:
            key += '.smoothed'

        fn = op.join(self.bids_folder, 'derivatives', key, f'sub-{self.subject}', f'ses-{session}', 'func', 
                f'sub-{self.subject}_ses-{session}_task-risk_space-T1w_desc-stims1_pe.nii.gz')

        im = image.load_img(fn)
        
        mask = self.get_volume_mask(roi=roi, session=session, epi_space=True)
        masker = NiftiMasker(mask_img=mask)

        data = pd.DataFrame(masker.fit_transform(im))

        return data

    def get_volume_mask(self, roi=None, session=None, epi_space=False):

        if roi is None:
            if epi_space:
                base_mask = op.join(self.bids_folder, 'derivatives', f'fmriprep/sub-{self.subject}/ses-{session}/func/sub-{self.subject}_ses-{session}_task-risk_run-1_space-T1w_desc-brain_mask.nii.gz')
                return image.load_img(base_mask)
            else:
                raise NotImplementedError
        elif roi.startswith('NPC'):
            mask = op.join(self.derivatives_dir
            ,'ips_masks',
            f'sub-{self.subject}',
            f'sub-{self.subject}_space-T1w_desc-{roi}.nii.gz'
            )
        elif roi.startswith('mpfc'):
            mask = op.join(self.derivatives_dir
            ,'mpfc_masks',
            f'sub-{self.subject}',
            f'sub-{self.subject}_space-T1w_{roi}_hemi-both.nii.gz'
            )
        else:
            raise NotImplementedError

        if epi_space:
            base_mask = op.join(self.bids_folder, 'derivatives', f'fmriprep/sub-{self.subject}/ses-{session}/func/sub-{self.subject}_ses-{session}_task-risk_run-1_space-T1w_desc-brain_mask.nii.gz')

            mask = image.resample_to_img(mask, base_mask, interpolation='nearest')

        return mask
    
    def get_prf_parameters_volume(self, session, 
            run=None,
            retroicor=False,
            smoothed=False,
            pca_confounds=False,
            denoise=False,
            cross_validated=True,
            natural_space=False,
            keys=None,
            roi=None,
            return_image=False,
            value=False):

        dir = 'encoding_model'
        if cross_validated:
            if run is None:
                raise Exception('Give run')

            dir += '.cv'

        if denoise:
            dir += '.denoise'
        if value:
            dir += '.value'

        if (retroicor) and (not denoise):
            raise Exception("When not using GLMSingle RETROICOR is *always* used!")

        if retroicor:
            dir += '.retroicor'
            
        if smoothed:
            dir += '.smoothed'

        if pca_confounds:
            dir += '.pca_confounds'
        if natural_space:
            dir += '.natural_space'
        parameters = []
        
        if keys is None:
            keys = ['mu', 'sd', 'amplitude', 'baseline']

        mask = self.get_volume_mask(session=session, roi=roi, epi_space=True)
        masker = NiftiMasker(mask)

        for parameter_key in keys:
            if cross_validated:
                fn = op.join(self.bids_folder, 'derivatives', dir, f'sub-{self.subject}', f'ses-{session}', 
                        'func', f'sub-{self.subject}_ses-{session}_run-{run}_desc-{parameter_key}.optim_space-T1w_pars.nii.gz')
            else:
                fn = op.join(self.bids_folder, 'derivatives', dir, f'sub-{self.subject}', f'ses-{session}', 
                        'func', f'sub-{self.subject}_ses-{session}_desc-{parameter_key}.optim_space-T1w_pars.nii.gz')
            
            pars = pd.Series(masker.fit_transform(fn).ravel())
            parameters.append(pars)
        
        parameters =  pd.concat(parameters, axis=1, keys=keys, names=['parameter'])

        if return_image:
            return masker.inverse_transform(parameters.T)

        return pd.concat(parameters, axis=1, keys=keys, names=['parameter'])
    
    def get_prf_parameters_surf(self, session, run=None, smoothed=False, cross_validated=False, hemi=None, mask=None, space='fsnative',
        parameters=None, key=None, nilearn=True):

        if mask is not None:
            raise NotImplementedError

        if parameters is None:
            parameter_keys = ['mu', 'sd',  'r2'] #'cvr2',
        else:
            parameter_keys = parameters

        if hemi is None:
            prf_l = self.get_prf_parameters_surf(session, 
                    run, smoothed, cross_validated, hemi='L',
                    mask=mask, space=space, key=key, parameters=parameters)
            prf_r = self.get_prf_parameters_surf(session, 
                    run, smoothed, cross_validated, hemi='R',
                    mask=mask, space=space, key=key, parameters=parameters)
            
            return pd.concat((prf_l, prf_r), axis=0, 
                    keys=pd.Index(['L', 'R'], name='hemi'))

        if key is None:
            if cross_validated:
                dir = 'encoding_model.cv.denoise'
            else:
                dir = 'encoding_model.denoise'

            if smoothed:
                dir += '.smoothed'

            dir += '.natural_space'
        else:
            dir = key
            print(dir)

        parameters = []
    
        for parameter_key in parameter_keys:
            if cross_validated:
                if nilearn:
                    fn = op.join(self.bids_folder, 'derivatives', dir, f'sub-{self.subject}', f'ses-{session}', 
                            'func', f'sub-{self.subject}_ses-{session}_run-{run}_desc-{parameter_key}.optim.nilearn_space-{space}_hemi-{hemi}.func.gii') # volume.
                else:
                    fn = op.join(self.bids_folder, 'derivatives', dir, f'sub-{self.subject}', f'ses-{session}', 
                            'func', f'sub-{self.subject}_ses-{session}_run-{run}_desc-{parameter_key}.volume.optim_space-{space}_hemi-{hemi}.func.gii')
            else:
                if nilearn:
                    fn = op.join(self.bids_folder, 'derivatives', dir, f'sub-{self.subject}', f'ses-{session}', 
                            'func', f'sub-{self.subject}_ses-{session}_desc-{parameter_key}.optim.nilearn_space-{space}_hemi-{hemi}.func.gii') # .volume
                else:
                    fn = op.join(self.bids_folder, 'derivatives', dir, f'sub-{self.subject}', f'ses-{session}', 
                            'func', f'sub-{self.subject}_ses-{session}_desc-{parameter_key}.volume.optim_space-{space}_hemi-{hemi}.func.gii')

            pars = pd.Series(surface.load_surf_data(fn))
            pars.index.name = 'vertex'

            parameters.append(pars)

        return pd.concat(parameters, axis=1, keys=parameter_keys, names=['parameter'])
    
    def get_surf_info(self):
        info = {'L':{}, 'R':{}}

        for hemi in ['L', 'R']:

            fs_hemi = {'L':'lh', 'R':'rh'}[hemi]

            info[hemi]['inner'] = op.join(self.bids_folder, 'derivatives', 'fmriprep', f'sub-{self.subject}', 'ses-1', 'anat', f'sub-{self.subject}_ses-1_hemi-{hemi}_smoothwm.surf.gii')
            info[hemi]['mid'] = op.join(self.bids_folder, 'derivatives', 'fmriprep', f'sub-{self.subject}', 'ses-1', 'anat', f'sub-{self.subject}_ses-1_hemi-{hemi}_midthickness.surf.gii')
            info[hemi]['outer'] = op.join(self.bids_folder, 'derivatives', 'fmriprep', f'sub-{self.subject}', 'ses-1', 'anat', f'sub-{self.subject}_ses-1_hemi-{hemi}_pial.surf.gii')
            info[hemi]['inflated'] = op.join(self.bids_folder, 'derivatives', 'fmriprep', f'sub-{self.subject}', 'ses-1', 'anat', f'sub-{self.subject}_ses-1_hemi-{hemi}_inflated.surf.gii')
            info[hemi]['curvature'] = op.join(self.bids_folder, 'derivatives', 'freesurfer', f'sub-{self.subject}', 'surf', f'{fs_hemi}.curv')

            for key in info[hemi]:
                assert(os.path.exists(info[hemi][key])), f'{info[hemi][key]} does not exist'

        return info
    
    def get_fmri_events(self, session, runs=None, value = False):

        if runs is None:
            runs = range(1,7)

        value_n = 'value_' if value else ''

        behavior = []
        for run in runs:
            behavior.append(pd.read_table(op.join(
                self.bids_folder, f'sub-{self.subject}/ses-{session}/func/sub-{self.subject}_ses-{session}_task-risk_run-{run}_{value_n}events.tsv')))

        behavior = pd.concat(behavior, keys=runs, names=['run'])
        behavior = behavior.reset_index().set_index(
            ['run', 'trial_type'])


        stimulus1 = behavior.xs('stimulus 1', 0, 'trial_type', drop_level=False).reset_index('trial_type')[['onset', 'trial_nr', 'trial_type']]
        stimulus1['duration'] = 0.6
        stimulus1['trial_type'] = stimulus1.trial_nr.map(lambda trial: f'trial_{trial:03d}_n1')

        
        stimulus2 = behavior.xs('stimulus 2', 0, 'trial_type', drop_level=False).reset_index('trial_type')[['onset', 'trial_nr', 'trial_type', 'n2']]
        stimulus2['duration'] = 0.6
        stimulus2['trial_type'] = stimulus2.n2.map(lambda n2: f'n2_{int(n2)}')

        events = pd.concat((stimulus1, stimulus2)).sort_index()

        return events

    def get_target_dir(subject, session, sourcedata, base, modality='func'):
        target_dir = op.join(sourcedata, 'derivatives', base, f'sub-{subject}', f'ses-{session}',
                            modality)

        if not op.exists(target_dir):
            os.makedirs(target_dir)

        return target_dir
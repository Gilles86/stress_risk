from nipype.interfaces.matlab import MatlabCommand
import nipype
from nipype.interfaces import spm
from nipype import Node
import os.path as op
import shutil

import socket

hostname = socket.gethostname()

if hostname == 'mr-02':
    MatlabCommand.set_default_paths('/home/ubuntu/matlab/spm12') # 
    bids_folder = '/mnt_01/ds-stressrisk' 
elif hostname == 'Econ117':
    MatlabCommand.set_default_paths('/Users/mrenke/matlab/spm12')
    MatlabCommand.set_default_matlab_cmd('/Applications/MATLAB_R2021b.app/bin/matlab')
    spm.SPMCommand.set_mlab_paths(matlab_cmd="/Applications/MATLAB_R2021b.app/bin/matlab") # error during spm.EstimateModel, solved: https://neurostars.org/t/nipype-spm-spmcommand-version-does-not-return-anything-on-mac/2871
    bids_folder = '/Volumes/mrenkeED/data/ds-stressrisk'


def smooth_image(sub, ses, run, bids_folder=bids_folder):
    
    unsmootehd_nifti_file = op.join(bids_folder, 'derivatives/spm_nipype', f'sub-{sub}', f'ses-{ses}', f'sub-{sub}_ses-{ses}_task-risk_run-{run}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii')

    if not op.isfile(unsmootehd_nifti_file):
        print(" unsmoothed file does also not exist")
        return   
    
    smooth = Node(interface=spm.Smooth(), name="smooth")
    smooth.inputs.in_files = unsmootehd_nifti_file
    smooth.inputs.fwhm = [6, 6 ,6]
    res_smooth = smooth.run()

    # now move to spm_nipype sub flder
    out_file = res_smooth.outputs.smoothed_files
    new_out_path = op.join(bids_folder,'derivatives/spm_nipype',f'sub-{sub}', f'ses-{ses}')
    shutil.move(out_file, op.join(new_out_path, out_file.split('/')[-1]))



def get_subject_info(subject):
    from glob import glob
    import numpy as np
    import pandas as pd
    from scipy import io, stats
    from nipype.interfaces.base import Bunch
    import os.path as op
    
    bids_folder = '/mnt_01/ds-stressrisk' 
    sub = subject

    subject_info = []
    functional_runs = []
    for ses in [1,2]:
        for run in range(1, 7):
            run_ses_i = (ses - 1)*6 + run
            
            # regressors (confounds + physio)
            confounds = pd.read_csv(op.join(bids_folder, 'derivatives/fmriprep',f'sub-{sub}', f'ses-{ses}', 'func', 
                            f'sub-{sub}_ses-{ses}_task-risk_run-{run}_desc-confounds_timeseries.tsv'), sep='\t')
            confound_names = ["trans_x","trans_y","trans_z","rot_x","rot_y","rot_z","a_comp_cor_00","a_comp_cor_02","a_comp_cor_03","a_comp_cor_04"]
            confounds = confounds.loc[:, confound_names]
            fn_physio = op.join(bids_folder, 'derivatives/physiotoolbox',f'sub-{sub}', f'ses-{ses}', 'func', 
                                f'sub-{sub}_ses-{ses}_task-task_run-{run}_desc-retroicor_output.mat') # task-taks (not risk) 
            physio = io.loadmat(fn_physio, simplify_cells=True)["physio"]["model"]
            physio = pd.DataFrame(
                data=physio["R"],
                columns=physio["R_column_names"])
            regressors = pd.concat([confounds, physio], axis=1)
            regressor_names = regressors.columns.values.tolist()

            # events + pmods
            df_events = pd.read_csv(op.join(bids_folder, f'sub-{sub}', f'ses-{ses}', 'func', f'sub-{sub}_ses-{ses}_task-risk_run-{run}_events.tsv'), sep='\t')
            df_events.set_index(['trial_nr', 'trial_type'], inplace=True) # only look at second option
            
            df_events_num1 = df_events.xs('stimulus 1',0,'trial_type')[['onset','prob1','n1']]
            df_risky_num1 = df_events_num1[df_events_num1['prob1'] == 0.55]
            df_safe_num1 = df_events_num1[df_events_num1['prob1'] == 1]   
            
            df_events_num2 = df_events.xs('stimulus 2',0,'trial_type')[['onset','prob2','n2']]
            df_risky_num2 = df_events_num2[df_events_num2['prob2'] == 0.55]
            df_safe_num2 = df_events_num2[df_events_num2['prob2'] == 1]

            pmod = [
                Bunch(name=['num1_risky'], param=[df_risky_num1['n1'].values.tolist()], poly=[1]),
                Bunch(name=['num1_safe'],param=[df_safe_num1['n1'].values.tolist()], poly=[1]),
                Bunch(name=['num2_risky'], param=[df_risky_num2['n2'].values.tolist()], poly=[1]),
                Bunch(name=['num2_safe'],param=[df_safe_num2['n2'].values.tolist()], poly=[1])]
            onsets = [
                df_risky_num1['onset'].values.tolist(), 
                df_safe_num1['onset'].values.tolist(),
                df_risky_num2['onset'].values.tolist(), 
                df_safe_num2['onset'].values.tolist()]

            durations = [(np.ones(len(df_risky_num1))* 0.6).tolist(), 
                         (np.ones(len(df_safe_num1))* 0.6).tolist(),
                         (np.ones(len(df_risky_num2))* 0.6).tolist(), 
                         (np.ones(len(df_safe_num2))* 0.6).tolist()]

            # put all together
            conditions = [f'risky_num1_ses{ses}', f'safe_num1_ses{ses}', f'risky_num2_ses{ses}', f'safe_num2_ses{ses}']

            nifti_file =  op.join(bids_folder,'derivatives/spm_nipype', f'sub-{sub}', f'ses-{ses}', f'ssub-{sub}_ses-{ses}_task-risk_run-{run}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii')
            if not op.isfile(nifti_file):
                print(f'{nifti_file} does not exist, probably smoothing did not work')
            else:
                functional_run = glob(nifti_file)[0]
                functional_runs.append(functional_run)
                subject_info.insert(
                    run_ses_i - 1,
                    Bunch(
                        conditions=conditions,
                        onsets=onsets,
                        durations=durations,
                        pmod=pmod,
                        tmod=None,
                        orth=['No']*len(conditions),
                        regressors=regressors.values.T.tolist(),
                        regressor_names=regressor_names,
                    ),
            )

    return subject_info, functional_runs

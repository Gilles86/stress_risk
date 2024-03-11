from nilearn import plotting
from os.path import join as opj
import os.path as op
import json
import os
from nipype.interfaces.base import Bunch
import nipype.interfaces.spm as spm
from nipype.interfaces.spm import (
    Level1Design,
    EstimateModel,
    EstimateContrast,
    SPMCommand,
    Info,
    model,
)
from nipype.interfaces.matlab import MatlabCommand
from nipype.interfaces.freesurfer import FSCommand
from nipype.algorithms.modelgen import SpecifySPMModel, SpecifyModel
from nipype.interfaces.utility import Function, IdentityInterface
from nipype.interfaces.io import SelectFiles, DataSink
from nipype import Workflow, Node
from bids.layout import BIDSLayout
from glob import glob
from scipy import io, stats
from itertools import chain
import pandas as pd
import numpy as np
#import pytest as pt
import nibabel as nb
import nipype
import argparse

MatlabCommand.set_default_paths('/home/ubuntu/matlab/spm12') # 
print(spm.SPMCommand().version)
bids_folder = '/mnt_01/ds-stressrisk' 

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

            #nifit_file = op.join(bids_folder,'derivatives/fmriprep',f'sub-{sub}', f'ses-{ses}', 'func',)
            nifti_file =  op.join(bids_folder,'derivatives/spm_nipype', f'sub-{sub}', f'ses-{ses}', f'ssub-{sub}_ses-{ses}_task-risk_run-{run}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii')
            functional_run = glob(nifti_file)[0]
            functional_runs.append(functional_run)

    return subject_info, functional_runs

def get_contrasts(subject_info):
    from nipype.interfaces.spm import EstimateContrast
    import os

    pmod_names = ['risky_num2_ses1xnum2_risky^1','risky_num2_ses2xnum2_risky^1', # 'group by riksy/safe for easier indexiing
                'safe_num2_ses1xnum2_safe^1','safe_num2_ses2xnum2_safe^1']
    condition_names = ['risky_num2_ses1','risky_num2_ses2','safe_num2_ses1','safe_num2_ses2']
    
    # same for both sessions
    con01 = ('num2_risky_int_bothSes', 'T', condition_names[0:2], [1/2. , 1/2.]) #['num2_risky', 'T', [condition_names[0]], [1.]]
    con02 = ('num2_safe_int_bothSes', 'T', condition_names[2:4], [1/2. , 1/2.])#['num2_safe', 'T', [condition_names[1]], [1.]]  
    con03 = ('num2_risky_pmod_bothSes', 'T', pmod_names[0:2], [1/2. , 1/2.]) #['num2_risky', 'T', [condition_names[0]], [1.]]
    con04 = ('num2_safe_pmod_bothSes', 'T', pmod_names[2:4], [1/2. , 1/2.])#['num2_safe', 'T', [condition_names[1]], [1.]]
    
    # difference between sessions
    con05 = ('num2_risky_int_sesDif', 'T', condition_names[0:2], [-1/2. , 1/2.]) #['num2_risky', 'T', [condition_names[0]], [1.]]
    con06 = ('num2_safe_int_sesDif', 'T', condition_names[2:4], [-1/2. , 1/2.])#['num2_safe', 'T', [condition_names[1]], [1.]]  
    con07 = ('num2_risky_sesDif', 'T', pmod_names[0:2], [-1/2. , 1/2.]) #['num2_risky', 'T', [condition_names[0]], [1.]]
    con08 = ('num2_safe_sesDif', 'T', pmod_names[2:4], [-1/2. , 1/2.])#['num2_safe', 'T', [condition_names[1]], [1.]]
       
    con_list = [con01, con02, con03, con04, con05,con06, con07, con08]
    
    return con_list



### --- main ------ 
def main(bids_folder=bids_folder, base_dir="/mnt_01/stressrisk_wf/spm_nipype", Nslices=40, refSlice=20):
    layout = BIDSLayout(bids_folder, derivatives=True)

    # list of subject identifiers
    subject_list = layout.get_subjects()
    subject_list = subject_list[:2]
    #subject_list = [sub for sub in subject_list if int(sub) not in [8, 13, 16, 31, 32, 44]] # remove subs
    with open(op.join(bids_folder, 'sub-01', 'ses-1','func', 'sub-01_ses-1_task-risk_run-1_bold.json'),"rt") as fp:
        task_info = json.load(fp)
    TR = task_info["RepetitionTime"]

    infosource = Node(
        IdentityInterface(
            fields=[
                "subject_id",
            ],
        ),
        name="infosource",
    )
    infosource.iterables = [
        ("subject_id", subject_list),
    ]

    getsubjectinfo = Node(
        Function(
            input_names=["subject"],
            output_names=["subject_info", "functional_runs"],
            function=get_subject_info,
        ),
        name="getsubjectinfo",
    )
    getcontrasts = Node(
        Function(
            input_names=["subject_info"],
            output_names=["contrasts"],
            function=get_contrasts,
        ),
        name="getcontrasts",
    )
    modelspec = Node(
        SpecifySPMModel(
            concatenate_runs=False,
            input_units="secs",
            output_units="secs",
            time_repetition=TR,
            high_pass_filter_cutoff=128,
        ),
        name="modelspec",
    )

    level1design = Node(
        Level1Design(
            bases={"hrf": {"derivs": [0, 0]}},
            timing_units="secs",
            interscan_interval=TR,
            model_serial_correlations="AR(1)",
            microtime_resolution=Nslices,
            microtime_onset=refSlice,
            flags={"mthresh": 0.8, "globalnorm": "None"},
            #mask_image="/mnt/d/multlearn-sns/SPM/mask_ICV.nii",
            volterra_expansion_order=1,
        ),
        name="level1design",
    )
    level1estimate = Node(
        EstimateModel(estimation_method={"Classical": 1}, write_residuals=False),
        name="level1estimate",
    )
    level1conest = Node(EstimateContrast(), name="level1conest")

    output_dir = 'model1'
    working_dir = 'workingdir'
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    datasink = Node(DataSink(base_directory=base_dir,
                         container=output_dir),
                name="datasink")
    substitutions = [('_subject_id_', 'sub-')]
    subjFolders = [('_sub-%s' % (sub), 'sub-%s' % (sub))
                for sub in subject_list]
    substitutions.extend(subjFolders)
    datasink.inputs.substitutions = substitutions
    
    first_level_wf = Workflow(name="first_level_wf", base_dir=os.path.join(base_dir, working_dir))


    # Connect the nodes
    first_level_wf.connect(
        [
            (infosource, getsubjectinfo, [("subject_id", "subject")]),
            (
                getsubjectinfo,
                modelspec,
                [
                    ("subject_info", "subject_info"),
                    ("functional_runs", "functional_runs"),
                ],
            ),
            (modelspec, level1design, [("session_info", "session_info")]),
            (
                level1design,
                level1estimate,
                [("spm_mat_file", "spm_mat_file")],
            ),
            (getsubjectinfo, getcontrasts, [("subject_info", "subject_info")]),
              # Connect level1design to level1estimate
            (
                getcontrasts,
                level1conest,
                [("contrasts", "contrasts")],
            ),  # Connect the contrasts to EstimateContrast
            (
                level1estimate,
                level1conest,
                [
                    ("spm_mat_file", "spm_mat_file"),
                    ("beta_images", "beta_images"),
                    ("residual_image", "residual_image"),
                ],
            ),
            (level1conest, datasink, [('spm_mat_file', '1stLevel.@spm_mat'),
                                              ('spmT_images', '1stLevel.@T'),
                                              ('con_images', '1stLevel.@con'),
                                              ]),
        ]
    )

    first_level_wf.config["logging"] = {
        "workflow_level": "DEBUG",
        "filemanip_level": "DEBUG",
        "interface_level": "DEBUG",
        "log_to_file": "True",
        "log_directory": "/output/log_folder",
    }

    first_level_wf.run('MultiProc', plugin_args={'n_procs': 2})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("bids_folder", type=str, default="/mnt_01/ds-stressrisk")
    parser.add_argument("--base_dir", type=str, default="/mnt_01/stressrisk_wf/spm_nipype")
    parser.add_argument("--Nslices", type=int, default=40)
    parser.add_argument("--refSlice", type=int, default=20)

    args = parser.parse_args()

    main(args.bids_folder, base_dir=args.base_dir,Nslices=args.Nslices, refSlice=args.refSlice)

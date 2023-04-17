%% SPM smoothing (preproc) and 1st level 
% need event.txt files created firsttf

spm('defaults','fmri');
spm_get_defaults('cmdline',true);
spm_jobman('initcfg');

bids_folder = '/Volumes/mrenkeED/data/ds-stressrisk'

subList = dir(strcat(bids_folder, "/sub-*"));
subList = {subList.name};

sesList = {'ses-1', 'ses-2'}

clear matlabbatch

%% gunzip loop over all subjects and sessions

pattern = '_space-MNI152NLin2009cAsym_desc-preproc_bold';

for sub = 6:numel(subList)
    for ses = 1:length(sesList)
       try
           data_path = strcat(bids_folder,'/derivatives/fmriprep/',subList{sub},'/',sesList{ses},'/func/');
           target_folder= strcat(bids_folder,'/derivatives', '/spm/',subList{sub},'/',sesList{ses});
           % mkdir(target_folder)
            strcat(subList{sub}, 'starting')

           for run= 1:6
    
            im_file = dir(strcat(data_path,'*run-', string(run),pattern, '*.nii.gz'));
            im_file = strcat(im_file.folder,'/',im_file.name);

            gunzip(im_file,target_folder)

           end

           strcat(subList{sub},' ', sesList{ses}, ' done')

       catch
           strcat(subList{sub}, ' ', sesList{ses}, ' problems')
       end

    end
end


%% smoothing loop over all subjects and sessions
 
for sub = 3:numel(subList)
    for ses = 1:length(sesList)
       try
           target_folder= strcat(bids_folder,'/derivatives', '/spm/',subList{sub},'/',sesList{ses});
            print(strcat(subList{sub}, 'starting'))

           for run= 1:6
            %smoothing
            f = spm_select('ExtList',target_folder,strcat('^*run-', string(run),'_space-MNI152NLin2009cAsym_desc-preproc_bold.*\.nii$') ,Inf); % fMRI       
            
            cd(target_folder)  

            clear matlabbatch
            matlabbatch{1}.spm.spatial.smooth.data = cellstr(f); %spm_file(f,'prefix','wa'));
            matlabbatch{1}.spm.spatial.smooth.fwhm = [8 8 8]; 
            matlabbatch{1}.spm.spatial.smooth.prefix = 'fwhm-8_';
            spm_jobman('run',matlabbatch);

            print(strcat(subList{sub}, 'done'))
            end
       end
    end
end

%% prepare confound (.multi_reg) file from motion and physio-retroicor data
sub = 1
ses = 1
run  = 1
motion_param = [];
R = [];
physio = [];
% LOAD physio data
physioR_file = (fullfile(bids_folder,'derivatives','physiotoolbox', subList{sub}, sesList{ses},'func', [subList{sub} '_' sesList{ses} '_task-task_run-' num2str(run) '_desc-retroicor_output.mat']));

    if ~exist(physioR_file, 'file')
        physio.model.R_column_names = [];
        physio.model.R = [];        
    else
        load(physioR_file); % gives physio object
    end
    
    % Load motion regressors
    file_motion = (fullfile(bids_folder,'derivatives','fmriprep', subList{sub}, sesList{ses},'func', [subList{sub} '_' sesList{ses} '_task-risk_run-' num2str(run) '_desc-confounds_timeseries.tsv']));
    motion_raw = tdfread(file_motion) 
    
    % Regress out the 6 std motion params and the three low frequency noise parameters
    motion_param = [motion_raw.trans_x motion_raw.trans_y motion_raw.trans_z motion_raw.rot_x motion_raw.rot_y motion_raw.rot_z ...
        motion_raw.cosine00 motion_raw.cosine01  motion_raw.cosine02];
    
    % Combine everything to nuisance regressors
    add_names = [];
    for ii = 1:numel(motion_param(1,:))
        add_names = [add_names; 'MotionReg_',num2str(ii)];
    end
    add_names =  cellstr(add_names)';
    
    names = [physio.model.R_column_names add_names ]  ;
    R = [physio.model.R motion_param ] ;
    %
    file_nuisance = fullfile(bids_folder,'derivatives','spm', subList{sub}, sesList{ses},[subList{sub} '_' sesList{ses} '_task-risk_run-' num2str(run) 'mult_reg_confounds.mat'])
    save(file_nuisance,'names', 'R');



%% 1st level


for sub = 1:numel(subList)
    for ses = 1:length(sesList)
       try
           target_folder= strcat(bids_folder,'/derivatives', '/spm/',sub,'/',ses);
           cd(target_folder)  

            matlabbatch{1}.cfg_basicio.file_dir.dir_ops.cfg_mkdir.parent = cellstr(target_folder);
            matlabbatch{1}.cfg_basicio.file_dir.dir_ops.cfg_mkdir.name = '1stlevel';
            %--------------------------------------------------------------------------
            matlabbatch{2}.spm.stats.fmri_spec.dir = cellstr(fullfile(target_folder,'1stlevel'));
            matlabbatch{2}.spm.stats.fmri_spec.timing.units = 'secs';


           for run= 1:6
            data_json = jsondecode(fileread(fullfile(bids_folder,  subList{sub}, sesList{ses}, 'func',[subList{sub} '_' sesList{ses} '_task-risk_run-' num2str(run) '_bold.json'])))
            TR = data_json.RepetitionTime;
            Nslices = numel(data_json.SliceTiming);
            refSlice = round(Nslices/2); % 

            matlabbatch{2}.spm.stats.fmri_spec.timing.RT = TR;        % interscan interval
            matlabbatch{2}.spm.stats.fmri_spec.timing.fmri_t = Nslices;
            matlabbatch{2}.spm.stats.fmri_spec.timing.fmri_t0 = refSlice;

            % 1st Model Specification
            clear matlabbatch
            ff = dir(strcat(target_folder,'/ssub*run-', string(run), '*.nii'));
            ff = spm_select('ExtList',target_folder,ff.name ,Inf);  
            
            file_nuisance = fullfile(bids_folder,'derivatives','spm', subList{sub}, sesList{ses},[subList{sub} '_' sesList{ses} '_task-risk_run-' num2str(run) 'mult_reg_confounds.mat']);

            onsets_n1 = load(strcat(target_folder,'/',sub,'_',ses,'_task-risk_run-',string(run),'_events_n1.txt'));
            onsets_n2 = load(strcat(target_folder,'/',sub,'_',ses,'_task-risk_run-',string(run),'_events_n2.txt'));

            matlabbatch{2}.spm.stats.fmri_spec.sess(run).scans = cellstr(spm_file(ff));
    
                    % Conditions --> columns in design matrix
                    matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).name = 'n1';
                    matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).onset = onsets_n1(:,1);    % vetor like data
                    matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).duration = 0.6;
                    matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).pmod.name = 'value';
                    matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).pmod.param = onsets_n1(:,3);
                    matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).pmod.poly = 1;
                    matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).orth = 0; % if additional pmod for same cond. set to 0
                    
    
                    matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).name = 'n2';
                    matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).onset = onsets_n2(:,1);    % vetor like data
                    matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).duration = 0.6;
                    matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).pmod.name = 'value';
                    matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).pmod.param = onsets_n2(:,3);
                    matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).pmod.poly = 1;
                    matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).orth = 0;

                matlabbatch{2}.spm.stats.fmri_spec.sess(run).multi_reg   = file_nuisance;
           
           end % of run loop

            matlabbatch{3}.spm.stats.fmri_est.spmmat = cellstr(fullfile(target_folder,'1stlevel','SPM.mat'));
            
            matlabbatch{3}.spm.stats.con.spmmat = cellstr(fullfile(target_folder,'1stlevel','SPM.mat'));
            matlabbatch{3}.spm.stats.con.consess{1}.tcon.name = 'n1_value';
            matlabbatch{3}.spm.stats.con.consess{1}.tcon.weights = [0 1 0 0 0];
            matlabbatch{3}.spm.stats.con.consess{2}.tcon.name = 'n2_value';
            matlabbatch{3}.spm.stats.con.consess{2}.tcon.weights= [0 0 0 1 0];
            
            spm_jobman('run',matlabbatch);

           catch
               strcat(sub,' ', ses)
       end
    end
end




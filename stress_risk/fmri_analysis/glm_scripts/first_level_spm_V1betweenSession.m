function first_level_spm_V1betweenSession(subject,bids_folder, model) %
   % extension of first_level_spm_V1.m to include both sessions and generate contrats between sessions 
   
   
   extra = '/event_files' % for EV, '' for EU
   model_name = ['1stlevel_' model '_betweenSession']
   target_folder= strcat(bids_folder,'/derivatives','/spm/',subject);
   cd(target_folder)  
   clear matlabbatch

    matlabbatch{1}.cfg_basicio.file_dir.dir_ops.cfg_mkdir.parent = cellstr(target_folder);
    matlabbatch{1}.cfg_basicio.file_dir.dir_ops.cfg_mkdir.name = model_name;
    %--------------------------------------------------------------------------
    matlabbatch{2}.spm.stats.fmri_spec.dir = cellstr(fullfile(target_folder,model_name));
    matlabbatch{2}.spm.stats.fmri_spec.timing.units = 'secs';

   sesList={'ses-1','ses-2'};
   for ses=1:2
       session = sesList{ses};
       source_folder= strcat(bids_folder,'/derivatives','/spm/',subject,'/',session);
       cd(source_folder)
        for run= 1:6
            %data_json = jsondecode(fileread(fullfile(bids_folder,  subject, session, 'func',[subject '_' session '_task-risk_run-' num2str(run) '_bold.json'])))
            TR = 2.2980 ; %data_json.RepetitionTime;
            Nslices =  39; %numel(data_json.SliceTiming);
            refSlice = 20; %round(Nslices/2); % 

            matlabbatch{2}.spm.stats.fmri_spec.timing.RT = TR;        % interscan interval
            matlabbatch{2}.spm.stats.fmri_spec.timing.fmri_t = Nslices;
            matlabbatch{2}.spm.stats.fmri_spec.timing.fmri_t0 = refSlice;

            % 1st Model Specification
            ff = dir(strcat(source_folder,'/ssub*run-', string(run), '*.nii'));
            ff = spm_select('ExtFPList',source_folder,ff.name ,Inf);  
            
            file_nuisance = fullfile(bids_folder,'derivatives','spm', subject, session,[subject '_' session '_task-risk_run-' num2str(run) '_mult-reg-confounds.mat']);

            onsets_n1 = load(strcat(source_folder,extra,'/',subject,'_',session,'_task-risk_run-',num2str(run),['_events_n1_' model '-1.txt']));
            onsets_n2 = load(strcat(source_folder,extra,'/',subject,'_',session,'_task-risk_run-',num2str(run),['_events_n2_' model '-1.txt']));
            onsets_diff = load(strcat(source_folder,extra,'/',subject,'_',session,'_task-risk_run-',num2str(run),['_events_diff_' model '-1.txt']));

            n_ses_run = (ses-1)*6 + run;
            matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).scans = cellstr(spm_file(ff));

                    % Conditions --> columns in design matrix
                    matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).cond(1).name = 'n1';
                    matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).cond(1).onset = onsets_n1(:,1);    % vetor like data
                    matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).cond(1).duration = 0.6;
                    matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).cond(1).pmod.name = 'value';
                    matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).cond(1).pmod.param = onsets_n1(:,3);
                    matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).cond(1).pmod.poly = 1;
                    matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).cond(1).orth = 0; % if additional pmod for same cond. set to 0
                    

                    matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).cond(2).name = 'n2';
                    matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).cond(2).onset = onsets_n2(:,1);    % vetor like data
                    matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).cond(2).duration = onsets_diff(:,2); %reaction times
                    matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).cond(2).pmod.name = 'value';
                    matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).cond(2).pmod.param = onsets_n2(:,3);
                    matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).cond(2).pmod.poly = 1;
                    matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).cond(2).orth = 0;

                matlabbatch{2}.spm.stats.fmri_spec.sess(n_ses_run).multi_reg   = cellstr(file_nuisance);
        
        end % of run loop
    end % of session loop
    
    cd(target_folder)  
    matlabbatch{3}.spm.stats.fmri_est.spmmat = cellstr(fullfile(target_folder,model_name,'SPM.mat'));
    
    % automatically generate the contrast vectors dependant on the number
    % of regressors, dependant on the number of confounds from the multReg
    load(file_nuisance);
    n_cond_reg = 4; % 2 von n1, 2 from n2 (cond, value, diff-choice)
    n_conf = size(R,2);
    N_runs = 12;
    n_reg = (n_cond_reg + n_conf) * N_runs + N_runs % N_runs was 6 before.....

    y = zeros(1, n_reg); 
    v1_i_both = y; v1_p_both = y; v2_i_both = y; v2_p_both = y; % intercept and pmod
    v1_i_dif = y; v1_p_dif = y; v2_i_dif = y; v2_p_dif = y;

    %session 1
    x1 = 1:n_cond_reg + n_conf:n_reg-N_runs; % v1 event
    x2 = 2:n_cond_reg + n_conf:n_reg-N_runs; % v1 pmod
    x3 = 3:n_cond_reg + n_conf:n_reg-N_runs; % v2 event
    x4 = 4:n_cond_reg + n_conf:n_reg-N_runs; % v2 pmod

    %session 2
    x5 = 5:n_cond_reg + n_conf:n_reg-N_runs; % v1 event
    x6 = 6:n_cond_reg + n_conf:n_reg-N_runs; % v1 pmod
    x7 = 7:n_cond_reg + n_conf:n_reg-N_runs; % v2 event
    x8 = 8:n_cond_reg + n_conf:n_reg-N_runs; % v2 pmod

    % v1 event
    v1_i_both(x1) = 1; v1_i_both(x5)=1; 
    v1_i_dif(x1) = 1; v1_i_dif(x5)=-1;
    % v1 pmod
    v1_p_both(x2) = 1; v1_p_both(x6)=1; 
    v1_p_dif(x2) = 1; v1_p_dif(x6)=-1;
    % v2 event
    v2_i_both(x3) = 1; v2_i_both(x7)=1;
    v2_i_dif(x3) = 1; v2_i_dif(x7)=-1;
    % v2 pmod
    v2_p_both(x4) = 1; v2_p_both(x8)=1;
    v2_p_dif(x4) = 1; v2_p_dif(x8)=-1;
     
    matlabbatch{4}.spm.stats.con.spmmat = cellstr(fullfile(target_folder,model_name,'SPM.mat'));
    

    matlabbatch{4}.spm.stats.con.consess{1}.tcon.name = 'v1_intercept_both';
    matlabbatch{4}.spm.stats.con.consess{1}.tcon.weights = v1_i_both;
    matlabbatch{4}.spm.stats.con.consess{2}.tcon.name = 'v1_pmod_both';
    matlabbatch{4}.spm.stats.con.consess{2}.tcon.weights = v1_p_both;
    matlabbatch{4}.spm.stats.con.consess{3}.tcon.name = 'v2_intercept_both';
    matlabbatch{4}.spm.stats.con.consess{3}.tcon.weights = v2_i_both;
    matlabbatch{4}.spm.stats.con.consess{4}.tcon.name = 'v2_pmod_both';
    matlabbatch{4}.spm.stats.con.consess{4}.tcon.weights = v2_p_both;
    matlabbatch{4}.spm.stats.con.consess{5}.tcon.name = 'v1_intercept_dif';
    matlabbatch{4}.spm.stats.con.consess{5}.tcon.weights = v1_i_dif;
    matlabbatch{4}.spm.stats.con.consess{6}.tcon.name = 'v1_pmod_dif';
    matlabbatch{4}.spm.stats.con.consess{6}.tcon.weights = v1_p_dif;
    matlabbatch{4}.spm.stats.con.consess{7}.tcon.name = 'v2_intercept_dif';
    matlabbatch{4}.spm.stats.con.consess{7}.tcon.weights = v2_i_dif;
    matlabbatch{4}.spm.stats.con.consess{8}.tcon.name = 'v2_pmod_dif';
    matlabbatch{4}.spm.stats.con.consess{8}.tcon.weights = v2_p_dif;
    
    
    spm_jobman('run',matlabbatch);
end
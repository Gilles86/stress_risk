function first_level_spm_Vchoice2(subject,session,bids_folder, model)
   % differentiates between trials where v2 or v1 was chosen, but models
   % everything at timepoint of v2 presentation (choice, duration
   % =choice-RT; pmod = v1 & v2
   % con = v1_ch, v1_unch; v2_ch; v2_unch; v1_ch_dif (v1_ch - v2_unch);
   % v2_ch_dif (v2_ch - v1_unch)
   
   
   model_name = ['1stlevel_' model]
   target_folder= strcat(bids_folder,'/derivatives','/spm/',subject,'/',session);
   cd(target_folder)  
   clear matlabbatch

    matlabbatch{1}.cfg_basicio.file_dir.dir_ops.cfg_mkdir.parent = cellstr(target_folder);
    matlabbatch{1}.cfg_basicio.file_dir.dir_ops.cfg_mkdir.name = model_name;
    %--------------------------------------------------------------------------
    matlabbatch{2}.spm.stats.fmri_spec.dir = cellstr(fullfile(target_folder,model_name));
    matlabbatch{2}.spm.stats.fmri_spec.timing.units = 'secs';


   for run= 1:6
    %data_json = jsondecode(fileread(fullfile(bids_folder,  subject, session, 'func',[subject '_' session '_task-risk_run-' num2str(run) '_bold.json'])))
    TR = 2.2980 ; %data_json.RepetitionTime;
    Nslices =  39; %numel(data_json.SliceTiming);
    refSlice = 20; %round(Nslices/2); % 

    matlabbatch{2}.spm.stats.fmri_spec.timing.RT = TR;        % interscan interval
    matlabbatch{2}.spm.stats.fmri_spec.timing.fmri_t = Nslices;
    matlabbatch{2}.spm.stats.fmri_spec.timing.fmri_t0 = refSlice;

    % 1st Model Specification
    ff = dir(strcat(target_folder,'/fwhm-8_sub*run-', string(run), '*.nii'));
    ff = spm_select('ExtList',target_folder,ff.name ,Inf);  
    
    file_nuisance = fullfile(bids_folder,'derivatives','spm', subject, session,[subject '_' session '_task-risk_run-' num2str(run) '_mult-reg-confounds.mat']);

    v1_chosen = load(strcat(target_folder,'/event_files/',subject,'_',session,'_task-risk_run-',num2str(run),['_events_v1-chosen_' model '.txt']));
    v2_chosen = load(strcat(target_folder,'/event_files/',subject,'_',session,'_task-risk_run-',num2str(run),['_events_v2-chosen_' model '.txt']));
    v1_unchosen = load(strcat(target_folder,'/event_files/',subject,'_',session,'_task-risk_run-',num2str(run),['_events_v1-unchosen_' model '.txt']));
    v2_unchosen = load(strcat(target_folder,'/event_files/',subject,'_',session,'_task-risk_run-',num2str(run),['_events_v2-unchosen_' model '.txt']));
   
    matlabbatch{2}.spm.stats.fmri_spec.sess(run).scans = cellstr(spm_file(ff));

            % Conditions --> columns in design matrix
            matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).name = 'v1_chosen';
            matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).onset = v2_unchosen(:,1);    % vetor like data
            matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).duration = v2_unchosen(:,2);
                matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).pmod.name = 'v1_chosen';
                matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).pmod(1).param = v1_chosen(:,3);
                matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).pmod(1).poly = 1;
                matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).pmod(2).name = 'v2_unchosen';
                matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).pmod(2).param = v2_unchosen(:,3);
                matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).pmod(2).poly = 1;
            matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(1).orth = 0;
            
            matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).name = 'v2_chosen';
            matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).onset = v2_chosen(:,1);    % vetor like data
            matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).duration = v2_chosen(:,2); %reaction times
                matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).pmod(1).name = 'v2_chosen';
                matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).pmod(1).param = v2_chosen(:,3);
                matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).pmod(1).poly = 1;
                matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).pmod(2).name = 'v1_unchosen';
                matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).pmod(2).param = v1_unchosen(:,3);
                matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).pmod(2).poly = 1;
            matlabbatch{2}.spm.stats.fmri_spec.sess(run).cond(2).orth = 0;


        matlabbatch{2}.spm.stats.fmri_spec.sess(run).multi_reg   = cellstr(file_nuisance);
   
   end % of run loop

    matlabbatch{3}.spm.stats.fmri_est.spmmat = cellstr(fullfile(target_folder,model_name,'SPM.mat'));
    
    % automatically generate the contrast vectors dependant on the number
    % of regressors, dependant on the number of confounds from the multReg
    load(file_nuisance);
    n_cond_reg = 6 % 2 x 3 (event, pmod1, pmod2)
    n_conf = size(R,2);
    n_reg = (n_cond_reg + n_conf) * 6 + 6;
    y = zeros(1, n_reg); n1 = y; n2 = y; n3 = y; n4 = y; n5 = y; n6=y;
    x1 = 2:n_cond_reg + n_conf:n_reg-6; % v1_ch
    x2 = 3:n_cond_reg + n_conf:n_reg-6; % v2_unch
    x3 = 5:n_cond_reg + n_conf:n_reg-6; % v2_ch
    x4 = 6:n_cond_reg + n_conf:n_reg-6; % v1_unch

    n1(x1) = 1; n2(x2)=1; n3(x3)=1; n4(x4)= 1;
    n5(x1) = 1; n5(x2) = -1; 
    n6(x3) = 1; n6(x4) = -1;    

    matlabbatch{4}.spm.stats.con.spmmat = cellstr(fullfile(target_folder,model_name,'SPM.mat'));
    matlabbatch{4}.spm.stats.con.consess{1}.tcon.name = 'v1_ch';
    matlabbatch{4}.spm.stats.con.consess{1}.tcon.weights = n1;
    matlabbatch{4}.spm.stats.con.consess{2}.tcon.name = 'v2_ch';
    matlabbatch{4}.spm.stats.con.consess{2}.tcon.weights = n2;
    matlabbatch{4}.spm.stats.con.consess{3}.tcon.name = 'v1_unch';
    matlabbatch{4}.spm.stats.con.consess{3}.tcon.weights = n3;
    matlabbatch{4}.spm.stats.con.consess{4}.tcon.name = 'v2_unch';
    matlabbatch{4}.spm.stats.con.consess{4}.tcon.weights = n4;
    matlabbatch{4}.spm.stats.con.consess{5}.tcon.name = 'v1_ch_dif';
    matlabbatch{4}.spm.stats.con.consess{5}.tcon.weights = n5;
    matlabbatch{4}.spm.stats.con.consess{6}.tcon.name = 'v2_ch_dif';
    matlabbatch{4}.spm.stats.con.consess{6}.tcon.weights = n6;
    
    spm_jobman('run',matlabbatch);
end
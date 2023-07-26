function first_level_spm(subject,session,bids_folder)
  % models plein numerosities (not EV/utility/NLC-estimate)

    target_folder= strcat(bids_folder,'/derivatives','/spm/',subject,'/',session);
   cd(target_folder)  
   clear matlabbatch

    matlabbatch{1}.cfg_basicio.file_dir.dir_ops.cfg_mkdir.parent = cellstr(target_folder);
    matlabbatch{1}.cfg_basicio.file_dir.dir_ops.cfg_mkdir.name = '1stlevel';
    %--------------------------------------------------------------------------
    matlabbatch{2}.spm.stats.fmri_spec.dir = cellstr(fullfile(target_folder,'1stlevel'));
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

    onsets_n1 = load(strcat(target_folder,'/',subject,'_',session,'_task-risk_run-',num2str(run),'_events_n1.txt'));
    onsets_n2 = load(strcat(target_folder,'/',subject,'_',session,'_task-risk_run-',num2str(run),'_events_n2.txt'));

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

        matlabbatch{2}.spm.stats.fmri_spec.sess(run).multi_reg   = cellstr(file_nuisance);
   
   end % of run loop

    matlabbatch{3}.spm.stats.fmri_est.spmmat = cellstr(fullfile(target_folder,'1stlevel','SPM.mat'));
    
    load(file_nuisance);
    n_conf = size(R,2);
    n_reg = (4 + n_conf) * 6 + 6;
    y = zeros(1, n_reg); n1 = y; n2 = y;
    x1 = 2:n_conf+4:n_reg-6; x2=4:n_conf+4:n_reg-6;
    n1(x1) = 1; n2(x2)=1;

    matlabbatch{4}.spm.stats.con.spmmat = cellstr(fullfile(target_folder,'1stlevel','SPM.mat'));
    matlabbatch{4}.spm.stats.con.consess{1}.tcon.name = 'n1_value';
    matlabbatch{4}.spm.stats.con.consess{1}.tcon.weights = n1;
    matlabbatch{4}.spm.stats.con.consess{2}.tcon.name = 'n2_value';
    matlabbatch{4}.spm.stats.con.consess{2}.tcon.weights = n2;
    
    spm_jobman('run',matlabbatch);
end
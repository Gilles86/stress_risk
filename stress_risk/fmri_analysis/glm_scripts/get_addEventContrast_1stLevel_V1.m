function get_addEventContrast_1stLevel_V1(subject,session,bids_folder, model)

   extra = '/event_files' % for EV, '' for EU
   model_name = ['1stlevel_' model '-1']
   target_folder= strcat(bids_folder,'/derivatives','/spm/',subject,'/',session);
   %cd(target_folder)  
   clear matlabbatch
    run=1
    file_nuisance = fullfile(bids_folder,'derivatives','spm', subject, session,[subject '_' session '_task-risk_run-' num2str(run) '_mult-reg-confounds.mat']);

    load(file_nuisance);
    n_cond_reg = 5; % 2 von n1, 3 from n2 (cond, value, diff-choice)
    n_conf = size(R,2);
    n_reg = (n_cond_reg + n_conf) * 6 + 6;
    y = zeros(1, n_reg); n1 = y; n2 = y; n3 = y;
    x1 = 1:n_cond_reg + n_conf:n_reg-6; 
    x2 = 3:n_cond_reg + n_conf:n_reg-6;

    n1(x1) = 1; n2(x2)=1; 

    matlabbatch{1}.spm.stats.con.spmmat = cellstr(fullfile(target_folder,model_name,'SPM.mat'));
    matlabbatch{1}.spm.stats.con.consess{1}.tcon.name = 'v1-event';
    matlabbatch{1}.spm.stats.con.consess{1}.tcon.weights = n1;
    matlabbatch{1}.spm.stats.con.consess{2}.tcon.name = 'v2-event';
    matlabbatch{1}.spm.stats.con.consess{2}.tcon.weights = n2;
    
    spm_jobman('run',matlabbatch);
end

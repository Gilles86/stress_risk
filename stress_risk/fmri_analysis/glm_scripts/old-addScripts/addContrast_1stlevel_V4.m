function addContrast_1stlevel_V4(subject,session,bids_folder, model)

   model_name = ['1stlevel_' model '-4']
   target_folder= strcat(bids_folder,'/derivatives','/spm/',subject,'/',session);
   cd(target_folder)  
   clear matlabbatch

    % automatically generate the contrast vectors dependant on the number
    % of regressors, dependant on the number of confounds from the multReg
    run = 1;
    file_nuisance = fullfile(bids_folder,'derivatives','spm', subject, session,[subject '_' session '_task-risk_run-' num2str(run) '_mult-reg-confounds.mat']);

    load(file_nuisance);
    n_cond_reg = 8; % 2*2 + 2*2 = (risky/safe * first/second) * (event, pmod1)
    n_conf = size(R,2);
    n_reg = (n_cond_reg + n_conf) * 6 + 6
    y = zeros(1, n_reg); n1 = y; n2 = y; n3 = y; n4 = y;
    x1 = 1:n_cond_reg + n_conf:n_reg-6; % risky_first 
    x2 = 3:n_cond_reg + n_conf:n_reg-6; % risky_second
    x3 = 5:n_cond_reg + n_conf:n_reg-6; % safe_first
    x4 = 7:n_cond_reg + n_conf:n_reg-6; % safe_second

    n1(x1)=1; 
    n2(x2)=1; 
    n3(x3)=1; 
    n4(x4)= 1;

    matlabbatch{1}.spm.stats.con.spmmat = cellstr(fullfile(target_folder,model_name,'SPM.mat'));
    matlabbatch{1}.spm.stats.con.consess{1}.tcon.name = 'risky_first_event';
    matlabbatch{1}.spm.stats.con.consess{1}.tcon.weights = n1;
    matlabbatch{1}.spm.stats.con.consess{2}.tcon.name = 'risky_second_event';
    matlabbatch{1}.spm.stats.con.consess{2}.tcon.weights = n2;
    matlabbatch{1}.spm.stats.con.consess{3}.tcon.name = 'safe_first_event';
    matlabbatch{1}.spm.stats.con.consess{3}.tcon.weights = n3;
    matlabbatch{1}.spm.stats.con.consess{4}.tcon.name = 'safe_second_event';
    matlabbatch{1}.spm.stats.con.consess{4}.tcon.weights = n4;

    spm_jobman('run',matlabbatch);
end

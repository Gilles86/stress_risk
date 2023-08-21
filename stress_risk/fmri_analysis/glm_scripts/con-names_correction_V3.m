%% dsad

model = 'EV'
bids_folder = '/Volumes/mrenkeED/data/ds-stressrisk'
model_name = ['1stlevel_' model '-3']
subList = dir([bids_folder, '/sub-*'])
subList = {subList.name}

sesList={'ses-1','ses-2'}


%% loop

errorL = [];

for sub=5:numel(subList)
    for ses=1:2
    
      try 
        subject = subList{sub};
        session = sesList{ses};
    
        target_folder= strcat(bids_folder,'/derivatives','/spm/',subject,'/',session);
        
        % delete old contrast
        cd(fullfile(target_folder,model_name))
        load('SPM.mat')
        SPM.xCon= []
        save SPM SPM
        
        run=1 ; % andy run
        file_nuisance = fullfile(bids_folder,'derivatives','spm', subject, session,[subject '_' session '_task-risk_run-' num2str(run) '_mult-reg-confounds.mat']);
    
        load(file_nuisance);
        n_cond_reg = 10; % 2*2 + 2*3 (event, pmod1, pmod2)
        n_conf = size(R,2);
        n_reg = (n_cond_reg + n_conf) * 6 + 6
        y = zeros(1, n_reg); n1 = y; n2 = y; n3 = y; n4 = y; n5 = y; n6=y;
        x1 = 2:n_cond_reg + n_conf:n_reg-6; % v1_ch
        x2 = 4:n_cond_reg + n_conf:n_reg-6; % v1_unch
        x3 = 6:n_cond_reg + n_conf:n_reg-6; % v2_ch
        x4 = 7:n_cond_reg + n_conf:n_reg-6; % v2_ch_diff
        x5 = 9:n_cond_reg + n_conf:n_reg-6; % v2_unch
        x6 = 10:n_cond_reg + n_conf:n_reg-6; % v2_unch_diff
       
        n1(x1)=1; 
        n2(x2)=1; 
        n3(x3)=1; n4(x4)= 1;
        n5(x5)=1; n6(x6) = 1;
    
        clear matlabbatch
        matlabbatch{1}.spm.stats.con.spmmat = cellstr(fullfile(target_folder,model_name,'SPM.mat'));
        matlabbatch{1}.spm.stats.con.consess{1}.tcon.name = 'v1_ch';
        matlabbatch{1}.spm.stats.con.consess{1}.tcon.weights = n1;
        matlabbatch{1}.spm.stats.con.consess{2}.tcon.name = 'v1_unch';
        matlabbatch{1}.spm.stats.con.consess{2}.tcon.weights = n2;
        matlabbatch{1}.spm.stats.con.consess{3}.tcon.name = 'v2_ch';
        matlabbatch{1}.spm.stats.con.consess{3}.tcon.weights = n3;
        matlabbatch{1}.spm.stats.con.consess{4}.tcon.name = 'v2_ch_diff';
        matlabbatch{1}.spm.stats.con.consess{4}.tcon.weights = n4;
        matlabbatch{1}.spm.stats.con.consess{5}.tcon.name = 'v2_unch';
        matlabbatch{1}.spm.stats.con.consess{5}.tcon.weights = n5;
        matlabbatch{1}.spm.stats.con.consess{6}.tcon.name = 'v2_unch_diff';
        matlabbatch{1}.spm.stats.con.consess{6}.tcon.weights = n6;
        
        spm_jobman('run',matlabbatch);
      catch
        errorL = [errorL; subList{sub}];
      end

    end
end


 %% end
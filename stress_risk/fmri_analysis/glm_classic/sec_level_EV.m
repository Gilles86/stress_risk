% 2nd level SPM
clear matlabbatch

scans = {};
for sub=2:14 %numel(subList)
     for ses = 1:length(sesList)
        con_file = fullfile(bids_folder,'derivatives','spm',subList{sub},sesList{ses},'1stlevel','spmT_0001.nii');
        if isfile(con_file)
           scans{end+1,1} = [con_file ',1'];
        end
     end
end

matlabbatch{1}.spm.stats.factorial_design.dir = {fullfile(bids_folder,'derivatives/spm/2ndlevel')};
matlabbatch{1}.spm.stats.factorial_design.des.t1.scans = scans;
matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {}, 'cname', {}, 'iCFI', {}, 'iCC', {});
matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {}, 'iCFI', {}, 'iCC', {});
matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
matlabbatch{1}.spm.stats.factorial_design.masking.em = {''};
matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;


matlabbatch{2}.spm.stats.fmri_est.spmmat = {fullfile(bids_folder,'derivatives/spm/2ndlevel','SPM.mat')};
matlabbatch{2}.spm.stats.fmri_est.write_residuals = 0;
matlabbatch{2}.spm.stats.fmri_est.method.Classical = 1;

%spm_jobman('run',matlabbatch);
spm_jobman('interactive','matlabbatch');
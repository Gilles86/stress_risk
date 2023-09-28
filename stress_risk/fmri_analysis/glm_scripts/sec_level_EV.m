% 2nd level SPM

model = 'NLC-4'
specification = 'con' % 'con'

in_model_name = ['1stlevel_' model]

parent_out_folder= [model '_' specification '_2ndlevels'];

temp_SPM = load(fullfile(bids_folder,'derivatives','spm',subList{sub},sesList{ses},in_model_name, 'SPM.mat'))
get_names = @(s) s.name;
con_names = arrayfun(get_names, temp_SPM.SPM.xCon, 'UniformOutput', false)

for n=1:length(temp_SPM.SPM.xCon)
    
    num = num2str(n) %n1 or n2 value?
    
    out_folder= ['2ndlevel_' model '_' con_names{n}]

    clear matlabbatch

    scans = {};
    for sub=1:numel(subList)
         for ses = 1:length(sesList)
            con_file = fullfile(bids_folder,'derivatives','spm',subList{sub},sesList{ses},in_model_name,[specification '_000' num2str(n) '.nii']);
            if isfile(con_file)
               scans{end+1,1} = [con_file ',1'];
            end
         end
    end


    matlabbatch{1}.spm.stats.factorial_design.dir = {fullfile(bids_folder,'derivatives/spm/', parent_out_folder, out_folder)};
    matlabbatch{1}.spm.stats.factorial_design.des.t1.scans = scans;
    matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {}, 'cname', {}, 'iCFI', {}, 'iCC', {});
    matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {}, 'iCFI', {}, 'iCC', {});
    matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
    matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
    matlabbatch{1}.spm.stats.factorial_design.masking.em = {''};
    matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
    matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
    matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;


    matlabbatch{2}.spm.stats.fmri_est.spmmat = {fullfile(bids_folder,'derivatives/spm', parent_out_folder,out_folder,'SPM.mat')};
    matlabbatch{2}.spm.stats.fmri_est.write_residuals = 0;
    matlabbatch{2}.spm.stats.fmri_est.method.Classical = 1;
    
    matlabbatch{3}.spm.stats.con.spmmat = {fullfile(bids_folder,'derivatives/spm', parent_out_folder,out_folder,'SPM.mat')};
    matlabbatch{3}.spm.stats.con.consess{1}.tcon.name = con_names{n};
    matlabbatch{3}.spm.stats.con.consess{1}.tcon.weights = 1;

    spm_jobman('run',matlabbatch);
end

%spm_jobman('interactive','matlabbatch');
% 2nd level SPM

model = 'NLC-4'
specification = 'con' % 'con'

in_model_name = ['1stlevel_' model]

parent_out_folder= [model '_' specification '_2ndlevels'];


factor_1_name = 'group';
factor_1_level = 2;
factor_2_name = 'session';
factor_2_level = 2;
contrast_num = factor_1_level*factor_2_level;
%level_array = [1 1 1 2 2 2 3 3 3 4 4 4; 1 2 3 1 2 3 1 2 3 1 2 3];

group_mapping = csvread('/Volumes/mrenkeED/data/ds-stressrisk/derivatives/spm/group_mapping_spm.csv')

temp_SPM = load(fullfile(bids_folder,'derivatives','spm',subList{sub},sesList{ses},in_model_name, 'SPM.mat'))
get_names = @(s) s.name;
con_names = arrayfun(get_names, temp_SPM.SPM.xCon, 'UniformOutput', false)

n= 1 % con_names(1) = {'risky_first'}
    
out_folder= ['2ndlevel_' model '_' con_names{n} '_group-ses_fd']

clear matlabbatch


matlabbatch{1}.spm.stats.factorial_design.dir = {fullfile(bids_folder,'derivatives/spm/', parent_out_folder, out_folder)};
matlabbatch{1}.spm.stats.factorial_design.des.fd.scans = scans;

matlabbatch{1}.spm.stats.factorial_design.des.fd.fact(1).name = factor_1_name;
matlabbatch{1}.spm.stats.factorial_design.des.fd.fact(1).levels = factor_1_level;
matlabbatch{1}.spm.stats.factorial_design.des.fd.fact(2).name = factor_2_name;
matlabbatch{1}.spm.stats.factorial_design.des.fd.fact(2).levels = factor_2_level;


scans = {};
group_array = []
session_array = [] 
count = 1
for sub=1:numel(subList)
     for ses = 1:length(sesList)
        con_file = fullfile(bids_folder,'derivatives','spm',subList{sub},sesList{ses},in_model_name,[specification '_000' num2str(n) '.nii']);
        if isfile(con_file)
           group = group_mapping(str2num(subList{sub}(5:6))==group_mapping(:,2),  3);

           matlabbatch{1}.spm.stats.factorial_design.des.fd.icell(count).scans = {con_file};
           matlabbatch{1}.spm.stats.factorial_design.des.fd.icell(count).levels = [group ses];
           %scans{end+1,1} = [con_file ',1'];
           count = count + 1;
           group_array = [group_array group];
           session_array = [session_array ses];
        end
     end
end

level_array = [group_array; session_array];


    

    matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {}, 'cname', {}, 'iCFI', {}, 'iCC', {});
    matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {}, 'iCFI', {}, 'iCC', {});
    matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
    matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
    matlabbatch{1}.spm.stats.factorial_design.masking.em = {''};
    %matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
    %matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
    %matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;


    matlabbatch{2}.spm.stats.fmri_est.spmmat = {fullfile(bids_folder,'derivatives/spm', parent_out_folder,out_folder,'SPM.mat')};
    matlabbatch{2}.spm.stats.fmri_est.write_residuals = 0;
    matlabbatch{2}.spm.stats.fmri_est.method.Classical = 1;
    
    matlabbatch{3}.spm.stats.con.spmmat = {fullfile(bids_folder,'derivatives/spm', parent_out_folder,out_folder,'SPM.mat')};
    matlabbatch{3}.spm.stats.con.consess{1}.tcon.name = con_names{n};
    matlabbatch{3}.spm.stats.con.consess{1}.tcon.weights = 1;

    spm_jobman('run',matlabbatch);


%spm_jobman('interactive','matlabbatch');


% from https://github.com/phildean/SPM_fMRI_Example_Pipeline/blob/master/secondlevel_analysis.m
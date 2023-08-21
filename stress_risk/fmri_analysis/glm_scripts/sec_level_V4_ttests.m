% 2nd level SPM

model = 'NLC-4'

bids_folder = '/Volumes/mrenkeED/data/ds-stressrisk'
in_model_name = ['1stlevel_' model]

subList = dir([bids_folder, '/sub-*'])
subList = {subList.name}

specification = 'bothSess1stlevel_2sTTest'
parent_out_folder= [model '_' specification '_2ndlevels'];
group_mapping = csvread('/Volumes/mrenkeED/data/ds-stressrisk/derivatives/spm/group_mapping_spm.csv')


temp_SPM = load(fullfile(bids_folder,'derivatives','spm',subList{1},in_model_name, 'SPM.mat'))
get_names = @(s) s.name;
con_names = arrayfun(get_names, temp_SPM.SPM.xCon, 'UniformOutput', false)


%% 2-sample-TTest on 1stlevel GLMS with both sessions


for n=1:numel(con_names) % 'risky_first_event_ses2-ses1''risky_first_pmod_ses2-ses1'
    clear matlabbatch

    out_folder= ['2ndlevel_' model '_' con_names{n}]

    scans_g0 = {};
    subs_ind = group_mapping(group_mapping(:,3) == 0, 1) + 1; %  col-1 = indices compatible with subList
    for sub=1:numel(subs_ind)
        con_file = fullfile(bids_folder,'derivatives','spm',subList{subs_ind(sub)},in_model_name,['con_000' num2str(n) '.nii']);
        isfile(con_file)
        if isfile(con_file)
           scans_g0{end+1,1} = [con_file ',1'];
        end
    end

    scans_g1 = {}; 
    subs_ind = group_mapping(group_mapping(:,3) == 1, 1) + 1; % col-1 = indices compatible with subList
    for sub=1:numel(subs_ind)
        con_file = fullfile(bids_folder,'derivatives','spm',subList{subs_ind(sub)},in_model_name,['con_000' num2str(n) '.nii']);
        if isfile(con_file)
           scans_g1{end+1,1} = [con_file ',1'];
        end
    end

    matlabbatch{1}.spm.stats.factorial_design.dir = {fullfile(bids_folder,'derivatives/spm/', parent_out_folder, out_folder)};
    matlabbatch{1}.spm.stats.factorial_design.des.t2.scans1 = scans_g0;
    matlabbatch{1}.spm.stats.factorial_design.des.t2.scans2 = scans_g1;
    matlabbatch{1}.spm.stats.factorial_design.des.t2.dept = 0;
    matlabbatch{1}.spm.stats.factorial_design.des.t2.variance = 1;
    matlabbatch{1}.spm.stats.factorial_design.des.t2.gmsca = 0;
    matlabbatch{1}.spm.stats.factorial_design.des.t2.ancova = 0;
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
    
    %matlabbatch{3}.spm.stats.con.spmmat = {fullfile(bids_folder,'derivatives/spm', parent_out_folder,out_folder,'SPM.mat')};
    %matlabbatch{3}.spm.stats.con.consess{1}.tcon.name = con_names{n};
    %matlabbatch{3}.spm.stats.con.consess{1}.tcon.weights = 1;

    spm_jobman('run',matlabbatch);
end
%%

for n=1:numel(con_names) % 'risky_first_event_ses2-ses1''risky_first_pmod_ses2-ses1'
    clear matlabbatch

    out_folder= ['2ndlevel_' model '_' con_names{n}]


    matlabbatch{1}.spm.stats.con.spmmat = {fullfile(bids_folder,'derivatives/spm', parent_out_folder,out_folder,'SPM.mat')};
    matlabbatch{1}.spm.stats.con.consess{1}.tcon.name = [con_names{n} '_g1_1tt'];
    matlabbatch{1}.spm.stats.con.consess{1}.tcon.weights = [1 0];
    matlabbatch{1}.spm.stats.con.consess{2}.tcon.name = [con_names{n} '_g1_2tt'];
    matlabbatch{1}.spm.stats.con.consess{2}.tcon.weights = [1 -1];
    matlabbatch{1}.spm.stats.con.consess{3}.tcon.name = [con_names{n} '_g0_1tt'];
    matlabbatch{1}.spm.stats.con.consess{3}.tcon.weights = [0 1];
    matlabbatch{1}.spm.stats.con.consess{4}.tcon.name = [con_names{n} '_g0_2tt'];
    matlabbatch{1}.spm.stats.con.consess{4}.tcon.weights = [-1 1];

    spm_jobman('run',matlabbatch);
end

% from https://github.com/phildean/SPM_fMRI_Example_Pipeline/blob/master/secondlevel_analysis.m
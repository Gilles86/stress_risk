%%


%%
model = 'EV'
specification = ''

for num=1:3
    clear matlabbatch

    out_folder= ['2ndlevel_' model specification '_' num2str(num)]
    
    matlabbatch{1}.spm.stats.con.spmmat = {fullfile(bids_folder,'derivatives/spm/', out_folder,'SPM.mat')};
    matlabbatch{1}.spm.stats.con.consess{1}.tcon.name = ['v' num2str(num)] ;
    matlabbatch{1}.spm.stats.con.consess{1}.tcon.weights = 1;
    
    spm_jobman('run',matlabbatch);
end

%% 
% Load contrast map
V = spm_vol('/Volumes/mrenkeED/data/ds-stressrisk/derivatives/spm/2ndlevel_EU-1_3/con_0001.nii');
[Y, XYZ] = spm_read_vols(V);

load('/Volumes/mrenkeED/data/ds-stressrisk/derivatives/spm/2ndlevel_EU-1_3/SPM.mat');
% Extract number of subjects
N = SPM.nscan;

% Set up statistical threshold parameters
STAT = 'T'; % T-contrast
df = [1, N-1]; % Degrees of freedom for T-test
u = spm_u(0.05, numel(Y), 'T', [1, V.df]);

u = {3.09}; % Height threshold (T-value)

% Calculate FWEc-corrected p-value
%[~, ~, ~, FWEc_p] = spm_uc(u, df, STAT, V, 0);
FWEc_p = spm_uc(u, df, STAT, V, 0);

disp(['FWEc-corrected p-value: ' num2str(FWEc_p)]);


spm_write_filtered % https://andysbrainbook.readthedocs.io/en/latest/fMRI_Short_Course/fMRI_Appendices/Appendix_A_ClusterCorrection.html

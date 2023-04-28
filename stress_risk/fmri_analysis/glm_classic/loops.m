% loops
addpath('/Users/mrenke/git/stress_risk/stress_risk/fmri_analysis/glm_classic')

bids_folder = '/mnt/ds-stressrisk'

subList = dir([bids_folder, '/sub-*'])
subList = {subList.name}

sesList={'ses-1','ses-2'}


%% loop with errorlist
errorL = [];

for sub=1:numel(subList)
    for ses=1:2
       try       
        prep_multreg_mat_file(subList{sub},sesList{ses},bids_folder);
        target_folder= strcat(bids_folder,'/derivatives','/spm/',subList{sub},'/',sesList{ses});
            % check if smoothing already done fwhm-8_sub-03_ses-1_task-risk_run-1_space-MNI152NLin2009cAsym_desc-preproc_bold
            if ~isfile(fullfile(target_folder,['fwhm-8_' subList{sub} '_' sesList{ses} '_task-risk_run-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii']))
                smoothing_func(subList{sub},sesList{ses},bids_folder);
            end
            
            %1stlevel, remove old
            cd(target_folder)
            try
                rmdir('1stlevel','s')
            end
            
            first_level_spm(subList{sub},sesList{ses},bids_folder);

        catch
            [subList{sub} ' ' sesList{ses} 'problem']
            errorL = [errorL; subList{sub}];
        end
        
    end 
end


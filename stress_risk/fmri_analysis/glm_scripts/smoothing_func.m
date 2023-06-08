function smoothing_func(subject,session,bids_folder)
   
    target_folder= strcat(bids_folder,'/derivatives', '/spm/',subject,'/',session);
    strcat(subject, 'starting') %print
    cd(target_folder)  

   for run= 1:6
        %smoothing
        f = spm_select('ExtList',target_folder,strcat('^*run-', string(run),'_space-MNI152NLin2009cAsym_desc-preproc_bold.*\.nii$') ,Inf); % fMRI       

        clear matlabbatch
        matlabbatch{1}.spm.spatial.smooth.data = cellstr(f); %spm_file(f,'prefix','wa'));
        matlabbatch{1}.spm.spatial.smooth.fwhm = [8 8 8]; 
        matlabbatch{1}.spm.spatial.smooth.prefix = 'fwhm-8_';
        spm_jobman('run',matlabbatch);

   end
end


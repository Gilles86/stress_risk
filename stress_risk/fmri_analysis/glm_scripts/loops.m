% loops
% 1. create mulreg file necessary for 1stlevel analysis
% 2. different versions of 1stlevels

% general variable definitions
bids_folder = '/mnt/ds-stressrisk'

subList = dir([bids_folder, '/sub-*'])
subList = {subList.name}

sesList={'ses-1','ses-2'}



%% 1. 

for sub=1:4 %numel(subList)
    for ses=1:2
        try
            prep_multreg_mat_file(subList{sub},sesList{ses},bids_folder);
             % functions loops over the 6 runs
        catch
            [subList{sub} ' ' sesList{ses} 'problem']
        end
        
    end 
end

%% 2.0. plein numerosities + checks smootehd file + mulreg + deleting old folders (for more space on Volume (/mnt))

errorL = [];

for sub=1:numel(subList)
    for ses=1:2
       try       
        %prep_multreg_mat_file(subList{sub},sesList{ses},bids_folder);
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

%% 2.1. 1stlevel( - version 1) loop + deleting old folders (for more space on Volume (/mnt))

errorL = [];
model = 'NLC' % carefull, timing files are named inconsistently among different model types (e.g. '...n1_EV' vs ' '...n1-EU')

for sub=1:numel(subList)
    for ses=1:2
       try       
            target_folder= strcat(bids_folder,'/derivatives','/spm/',subList{sub},'/',sesList{ses});
            
            %1stlevel, remove old
            cd(target_folder)
            try
                rmdir('1stlevel_EV-1','s')
                %rmdir('1stlevel_EU-3','s')

            end
            
            first_level_spm_V1b(subList{sub},sesList{ses},bids_folder, model); % scirpt adds automatically '-1'

        catch
            [subList{sub} ' ' sesList{ses} 'problem']
            errorL = [errorL; subList{sub}];
        end
        
    end 
end


%% 2.2. 1stlevel( - version 2)

errorL = [];

%model = 'EV'
model='EV-2';

for sub=1:numel(subList)
    for ses=1:2
        try
            %first_level_spm_EVnoN2(subList{sub},sesList{ses},bids_folder,model);
            first_level_spm_Vchoice2(subList{sub},sesList{ses},bids_folder,model);
            
        catch
            errorL = [errorL; [subList{sub} num2str(ses)]];

        end
    end
end


%% 2.3.1stlevel( - version 3)

errorL_V = [];

model='EV'; % numer - 3 will be added automatically here

for sub=1:numel(subList)
    for ses=1:2
        try 
            target_folder= strcat(bids_folder,'/derivatives','/spm/',subList{sub},'/',sesList{ses});
            cd(target_folder)
            try
                rmdir('1stlevel_EV-1','s')
                rmdir('1stlevel_EV-2','s')

            end
            first_level_spm_Vchoice3b(subList{sub},sesList{ses},bids_folder,model);
            
        catch
            errorL_V = [errorL_V; [subList{sub} '-' num2str(ses)]];

        end
    end
end
%%



%%
            target_folder= strcat(bids_folder,'/derivatives','/spm/',subList{sub},'/',sesList{ses});
            cd(target_folder)
            try
                rmdir('1stlevel_NLC','s')
                rmdir('1stlevel','s')     
            end
%% 
%% 2.4.1stlevel( - version 4)

errorL_V = [];

model='NLC'; % numer - 3 will be added automatically here

for sub=1:numel(subList)
    for ses=1:2
        try 
            target_folder= strcat(bids_folder,'/derivatives','/spm/',subList{sub},'/',sesList{ses});
            cd(target_folder)
            try
                rmdir('1stlevel_NLC-4','s')
            end
            first_level_spm_V4(subList{sub},sesList{ses},bids_folder,model);
            
        catch
            errorL_V = [errorL_V; [subList{sub} '-' num2str(ses)]];

        end
    end
end

%% 2.4.1stlevel( - version 4 both sessions)

errorL_V = [];

model='NLC'; % numer - 3 will be added automatically here

for sub=2:numel(subList)
    for ses=1:2
        target_folder= strcat(bids_folder,'/derivatives','/spm/',subList{sub},'/',sesList{ses});
        cd(target_folder)
        try
            rmdir('1stlevel_NLC-4','s')
        end
    end
    
    try
        first_level_spm_V4_bothSessions(subList{sub},bids_folder,model);
            
    catch
            errorL_V = [errorL_V; [subList{sub} '-' num2str(ses)]];

    end
end

%%




%errorL = errorL_NLC
model = 'EV'
model='NLC-2';

for i=2:length(errorL)-1
    subject = errorL(i,1:6)
    session = ['ses-' errorL(i,7)]
    %first_level_spm_EVnoN2(subject,session,bids_folder,model);    
    first_level_spm_EUchoice(subject,session,bids_folder,model);

end

%%

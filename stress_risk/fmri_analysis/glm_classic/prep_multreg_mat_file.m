function prep_multreg_mat_file(subject,session,bids_folder)
% needs: subject as 'sub-XX', session as 'ses-X'
%   bids_folder /derivatives/physiotoolbox/sub-XX/ses-X/func/sub-XX_ses-X_task-task_run-X_desc-retroicor_output.mat
%   bids_folder /derivatives/fmriprep/sub-XX/ses-X/func/sub-XX_ses-X_task-task_run-X_desc-confounds_timeseries.tsv
% puts output.mat file into bids_folder /derivatives/spm/sub-XX/ses-X

    for run=1:6
        motion_param = [];
        R = [];
        physio = [];
        % LOAD physio data
        physioR_file = (fullfile(bids_folder,'derivatives','physiotoolbox', subject, session,'func', [subject '_' session '_task-task_run-' num2str(run) '_desc-retroicor_output.mat']));
        
            if ~exist(physioR_file, 'file')
                physio.model.R_column_names = [];
                physio.model.R = [];
                [subject '_' session '_'  num2str(run) ' no physio file']
            else
                load(physioR_file); % gives physio object
            end
            
            % Load motion regressors
            file_motion = (fullfile(bids_folder,'derivatives','fmriprep', subject, session,'func', [subject '_' session '_task-risk_run-' num2str(run) '_desc-confounds_timeseries.tsv']));
            motion_raw = tdfread(file_motion); 
            
            % Regress out the 6 std motion params and the three low frequency noise parameters
            motion_param = [motion_raw.global_signal motion_raw.trans_x  motion_raw.trans_y  motion_raw.trans_z  motion_raw.rot_x  motion_raw.rot_y  motion_raw.rot_z  motion_raw.a_comp_cor_00  motion_raw.a_comp_cor_01  motion_raw.a_comp_cor_02  motion_raw.a_comp_cor_03]; % motion_raw.dvars motion_raw.framewise_displacement   
            % old: [motion_raw.trans_x motion_raw.trans_y motion_raw.trans_z motion_raw.rot_x motion_raw.rot_y motion_raw.rot_z motion_raw.cosine00 motion_raw.cosine01  motion_raw.cosine02];
            
            % Combine everything to nuisance regressors
            add_names = [];
            for ii = 1:numel(motion_param(1,:))
                add_names = [add_names; 'MotionReg_',num2str(ii, '%02.f')];
            end
            add_names =  cellstr(add_names)';
            
            names = [physio.model.R_column_names add_names ]  ;
            R = [physio.model.R motion_param ] ;
            %
            file_nuisance = fullfile(bids_folder,'derivatives','spm', subject, session,[subject '_' session '_task-risk_run-' num2str(run) '_mult-reg-confounds.mat']);
            save(file_nuisance,'names', 'R');
    end
end

% prepare folder structure

subList_folder= '/mnt/ds-stressrisk/derivatives/spm';% Replace with the actual path to your BIDS folder

files = dir(subList_folder); % Get list of files in the folder
subFolders = {files(strncmp({files.name}, 'sub', 3)).name}; % Extract subfolder names using logical indexing and array indexing
subFolders = cellfun(@(x) x(5:6), subFolders, 'UniformOutput', false); % Extract 5th and 6th characters from subfolder names

bids_folder= '/mnt/ds-stressrisk';
errorL = [];
for sub = 1:length(subFolders)
    %mkdir(sprintf(strcat(bids_folder,'/sub-%s'),sub))
    for ses = 1:2
        %mkdir(sprintf(strcat(bids_folder,'/der/sub-%s/ses-%s/'),sub,ses))
        %mkdir(sprintf(strcat(bids_folder,'/sub-%s/ses-%s/func/'),sub,ses))
        mkdir(strcat(bids_folder,'/sub-',subFolders{sub},'/ses-',num2str(ses),'/func/'))
        mkdir(strcat(bids_folder,'/derivatives/fmriprep', '/sub-',subFolders{sub},'/ses-',num2str(ses),'/func/'))
    end
end

% copy physio files




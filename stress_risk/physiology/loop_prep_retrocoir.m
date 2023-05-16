% loop for running

bids_folder='/Volumes/mrenkeED/data/ds-stressrisk' % Replace with the actual path to your BIDS folder

files = dir(bids_folder); % Get list of files in the folder
subFolders = {files(strncmp({files.name}, 'sub', 3)).name}; % Extract subfolder names using logical indexing and array indexing
subFolders = cellfun(@(x) x(5:6), subFolders, 'UniformOutput', false); % Extract 5th and 6th characters from subfolder names

errorL = [];
for sub = 1:length(subFolders)
    for ses = 1:2
        try 
           prepare_retroicor(subFolders{sub},num2str(ses), bids_folder);
        catch
            errorL = [errorL; subFolders{sub}];
        end
    end
end





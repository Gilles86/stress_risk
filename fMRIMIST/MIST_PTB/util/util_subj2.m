
function [subj2] = util_subj2(show,pic_dir)

%==========================================================================
% [subj2] = util_subj2(show,pic_dir)
%
% show = true / false, show photos or not
% pic_dir = directories where photos are stored (fullfile(...))
%
% ask who subj2 is
% if we show pictures, check if picture exists, otherwise throw warning and
% return
%==========================================================================
% check subj2 input
% isabella.wagner@univie.ac.at
%==========================================================================

% open dialogue box

subj2 = inputdlg('Name of the second subject?');

% check

confirmation(subj2)

% check if photos should be included in paradigm

if show == true
    
    % go to pics directory and check if photos exist
    
    cd(pic_dir)
    
    clear f; f = dir('subj2*');
    
    clear names; for i = 1:numel(f); names{i} = f(i).name(7:end-4); end
    
    if ~ismember(subj2,names)
        
        waitfor(msgbox(sprintf('No pictures of %s found!',char(subj2))))
        
        warning('No pictures of %s found!',char(subj2))
        
        return;
        
    end
    
end

end

%%

function confirmation(subj2)

subj21 = inputdlg('CONFIRM: name of the second subject?');

while ~strcmp(subj2,subj21)
    
    waitfor(msgbox(sprintf('Inputs do not match!')))
    
    warning('Inputs do not match!')
    
    subj2 = inputdlg('What is the name of the second subject?');
    
    subj21 = inputdlg('CONFIRM: name of the second subject?');
    
end

end
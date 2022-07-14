
% file directory

parm.dirs.home = fileparts(which([parm.info.paradigm,'_run']));

addpath((parm.dirs.home)) 

% ----------------------------------------
% make the output directory
% ----------------------------------------

parm.dirs.time = fullfile(pwd,'MIST_PTB');

parm.dirs.out = fullfile(pwd,'MIST_PTB','logfiles');%fullfile(pwd,'logfiles');
%addpath((parm.dirs.out)) 
if ~exist(parm.dirs.out,'dir'); mkdir(parm.dirs.out); end 




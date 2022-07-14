
%==========================================================================
% save data to mat
% isabella.wagner@univie.ac.at
%==========================================================================

disp(['Saving to mat: ',fullfile(parm.dirs.out,[savename,'.mat'])])

save(fullfile(parm.dirs.out,[savename,'.mat']),'parm','log');
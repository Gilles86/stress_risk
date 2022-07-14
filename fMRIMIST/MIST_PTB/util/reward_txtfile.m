
%==========================================================================
% write tab-delimited text file
% isabella.wagner@univie.ac.at
%==========================================================================

fprintf('writing to text file. \n');

cd(parm.dirs.out)

filename = [savename,'.txt'];

fid = fopen(filename, 'w');

% ----------------------------------------
%(-) MRI triggers
% ----------------------------------------

if parm.info.MRI == true
    
    for trig = 1:parm.exp.startvol
        
        formatSpec = 'mritrigger    %f';
        fprintf(fid,formatSpec,log.times.mritrigger(trig))
        fprintf(fid,'\n');
        
    end
    
    formatSpec = 'firstpulse    %f';
    fprintf(fid,formatSpec,log.times.firstpulse)
    fprintf(fid,'\n');
    
end

% ----------------------------------------
%(-) start_time = first onset = 7th volume
% ----------------------------------------

formatSpec = 'start_exp    %f';
fprintf(fid,formatSpec,log.times.startexp)
fprintf(fid,'\n');

% ----------------------------------------
%(-) header info
% ----------------------------------------

clear hdr; hdr = fields(log.exp)';

hdr = [hdr, ...
    {'start_cue'},{'dur_cue'},...
    {'start_trial'},{'dur_trial'},...
    {'start_show'},{'dur_show'},...
    {'start_outcome'},{'dur_outcome'},...
    {'start_isi'},{'dur_isi'},...
    {'start_break'},{'dur_break'},...
    {'button'},{'button_stim'},...
    {'RT_first'},{'RT_last'}];

formatSpec = repmat('%s\t ', 1, length(hdr));
formatSpec(end:end+1) = '\n';
fprintf(fid, formatSpec, hdr{:});

% ----------------------------------------
%(-) data 
% ----------------------------------------

% start with log.exp fields

M = [];

fnames = fields(log.exp);

for f = 1:numel(fields(log.exp))
%     fnames{f}
    M = [M, log.exp.(fnames{f})];
    
end

% break is startbreak until end of cue for next block

dur_break = log.times.endbreakcue - log.times.startbreak;

% the rest

M = [M, ...
    log.times.startcue, log.dur.cue,...
    log.times.starttrial, log.dur.trial,...
    log.times.startfinselection, log.dur.finselection,...
    log.times.startout, log.dur.out,...
    log.times.startiti, log.dur.iti,...
    log.times.startbreak, dur_break,...
    log.resp.RTfirst, log.resp.RTfin];

dlmwrite(filename,M,'-append','delimiter','\t','precision', '%.2f');

% ----------------------------------------
%(-) end time 
% ----------------------------------------

% fprintf(fid,'\n');
% formatSpec = 'end_exp    %f';
% fprintf(fid,formatSpec,log.times.endend)
% fprintf(fid,'\n');

dlmwrite(filename,log.times.endend,'-append','delimiter','\t');

% ----------------------------------------
%(-) fclose all
% ----------------------------------------

fclose(fid);

fprintf('done.');

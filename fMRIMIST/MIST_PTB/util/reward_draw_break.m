
%==========================================================================
% draw break between blocks
% isabella.wagner@univie.ac.at
%==========================================================================

% insert the break

util_text(parm.ptb.scr.w,parm.ptb.scr.font,parm.ptb.scr.stimfont,parm.ptb.scr.white,1)

DrawFormattedText( parm.ptb.scr.w, '* * * *', 'center', 'center');

log.times.startbreak(curr.ct) = Screen('Flip',parm.ptb.scr.w);
log.all.events = [log.all.events, {'startbreak'}];
log.all.onsets = [log.all.onsets , log.times.startbreak(curr.ct)];

WaitSecs(parm.exp.breaktime - parm.exp.breakalert)

log.times.endbreak(curr.ct) = GetSecs;
log.all.events = [log.all.events, {'endbreak'}];
log.all.onsets = [log.all.onsets , log.times.endbreak(curr.ct)];

% if there are 5s to go, change color to alert subject

util_text(parm.ptb.scr.w,parm.ptb.scr.font,parm.ptb.scr.stimfont,parm.ptb.scr.green,1)

DrawFormattedText(parm.ptb.scr.w, '* * * *', 'center', 'center');

log.times.startbreakcue(curr.ct) = Screen('Flip',parm.ptb.scr.w);
log.all.events = [log.all.events, {'startbreakcue'}];
log.all.onsets = [log.all.onsets , log.times.startbreakcue(curr.ct)];

WaitSecs(parm.exp.breakalert)

log.times.endbreakcue(curr.ct) = GetSecs;
log.all.events = [log.all.events, {'endbreakcue'}];
log.all.onsets = [log.all.onsets , log.times.endbreakcue(curr.ct)];

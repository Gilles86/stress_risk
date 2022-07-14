
%==========================================================================
% draw the stimulus image in the center and the blank feedback response box
% nace.mikus@univie.ac.at
%==========================================================================


%% draw the equation

% Screen('FrameRect',  parm.ptb.scr.w, parm.ptb.scr.white, parm.ptb.img.equation_window, 6);
if respond_in_time

if curr.correct
util_text(parm.ptb.scr.w,parm.ptb.scr.font,parm.ptb.img.fontsize+20,parm.ptb.scr.green,1)

% DrawFormattedText(parm.ptb.scr.w, 'CORRECT', 'center', parm.ptb.scr.rect(4)/3 + 300);
DrawFormattedText(parm.ptb.scr.w, 'CORRECT', 'center', 'center');

else
util_text(parm.ptb.scr.w,parm.ptb.scr.font,parm.ptb.img.fontsize+20,parm.ptb.scr.red,1)

DrawFormattedText(parm.ptb.scr.w, 'WRONG!', 'center', 'center');

% Screen('Flip',parm.ptb.scr.w);    
    
end

else 
    util_text(parm.ptb.scr.w,parm.ptb.scr.font,parm.ptb.img.fontsize+20,parm.ptb.scr.red,1)

    DrawFormattedText(parm.ptb.scr.w, 'TIMED OUT!', 'center', 'center');

end
% 
% Screen('Flip',parm.ptb.scr.w);







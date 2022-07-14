
%==========================================================================
% draw the stimulus image in the center and the blank feedback response box
% nace.mikus@univie.ac.at
%==========================================================================


%% draw the equation

% Screen('FrameRect',  parm.ptb.scr.w, parm.ptb.scr.white, parm.ptb.img.equation_window, 6);

util_text(parm.ptb.scr.w,parm.ptb.scr.font, (parm.ptb.img.fontsize+20).*.9 ,parm.ptb.scr.white,1)

DrawFormattedText(parm.ptb.scr.w, equation_text, parm.ptb.img.equation_window(1)+20, parm.ptb.img.equation_window(4)-30);

% 
% Screen('Flip',parm.ptb.scr.w);







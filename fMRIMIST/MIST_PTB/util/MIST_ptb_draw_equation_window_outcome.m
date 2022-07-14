
%==========================================================================
% draw the stimulus image in the center and the blank feedback response box
% nace.mikus@univie.ac.at
%==========================================================================


%% draw the equation window
if curr.correct
    
Screen('FrameRect',  parm.ptb.scr.w, parm.ptb.scr.green, parm.ptb.img.equation_window, 10);


else
Screen('FrameRect',  parm.ptb.scr.w, parm.ptb.scr.red, parm.ptb.img.equation_window, 10);
   
end






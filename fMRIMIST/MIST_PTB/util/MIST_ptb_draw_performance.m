
%==========================================================================
% draw the stimulus image in the center and the blank feedback response box
% nace.mikus@univie.ac.at
%==========================================================================

%% draw the performance bar

Screen('FillRect', parm.ptb.scr.w, parm.ptb.scr.red, parm.ptb.img.performance_bar_red);
Screen('FillRect', parm.ptb.scr.w, parm.ptb.scr.yellow, parm.ptb.img.performance_bar_yellow);
Screen('FillRect', parm.ptb.scr.w, parm.ptb.scr.green, parm.ptb.img.performance_bar_green);

Screen('FrameRect', parm.ptb.scr.w, parm.ptb.scr.black, parm.ptb.img.performance_bar_red);
Screen('FrameRect', parm.ptb.scr.w, parm.ptb.scr.black, parm.ptb.img.performance_bar_yellow);
Screen('FrameRect', parm.ptb.scr.w, parm.ptb.scr.black, parm.ptb.img.performance_bar_green);

% 
% util_text(parm.ptb.scr.w,parm.ptb.scr.font,parm.ptb.img.fontsize,parm.ptb.scr.black,1)
% 
% for k = 1 : 10
%     Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.backgrd,  parm.ptb.img.slider(1) + (k-1)*parm.ptb.img.box_size, parm.ptb.img.slider(2) , parm.ptb.img.slider(1) + (k-1)*parm.ptb.img.box_size,  parm.ptb.img.slider(4) ,parm.ptb.img.box_line_width);
%     
%     DrawFormattedText(parm.ptb.scr.w, num2str(k-1), parm.ptb.img.slider(1) + (k-1)*parm.ptb.img.box_size + parm.ptb.img.box_size/2, parm.ptb.img.text_pos_y);
% 
% end

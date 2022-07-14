
%==========================================================================
% draw the stimulus image in the center and the blank feedback response box
% nace.mikus@univie.ac.at
%==========================================================================

%% draw the number keypad

Screen('FillRect', parm.ptb.scr.w, parm.ptb.scr.white, parm.ptb.img.slider )
Screen('FrameRect', parm.ptb.scr.w, parm.ptb.scr.black, parm.ptb.img.slider )

for k = 1 : 10
    if k-1 == response
        util_text(parm.ptb.scr.w,parm.ptb.scr.font,parm.ptb.img.fontsize+20,parm.ptb.scr.red,1)

         
        DrawFormattedText(parm.ptb.scr.w, num2str(k-1), parm.ptb.img.slider(1) + (k-1)*parm.ptb.img.box_size + parm.ptb.img.box_size/2 -15, parm.ptb.img.text_pos_y);
        
    else
        util_text(parm.ptb.scr.w,parm.ptb.scr.font,parm.ptb.img.fontsize,parm.ptb.scr.grey3,1)

         
        DrawFormattedText(parm.ptb.scr.w, num2str(k-1), parm.ptb.img.slider(1) + (k-1)*parm.ptb.img.box_size + parm.ptb.img.box_size/2  -15, parm.ptb.img.text_pos_y);
    end
    Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.black,  parm.ptb.img.slider(1) + (k-1)*parm.ptb.img.box_size, parm.ptb.img.slider(2) , parm.ptb.img.slider(1) + (k-1)*parm.ptb.img.box_size,  parm.ptb.img.slider(4) ,parm.ptb.img.box_line_width);
       
end
Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.black,  parm.ptb.img.slider(1) + 10*parm.ptb.img.box_size, parm.ptb.img.slider(2) , parm.ptb.img.slider(1) + 10*parm.ptb.img.box_size,  parm.ptb.img.slider(4) ,parm.ptb.img.box_line_width);
    





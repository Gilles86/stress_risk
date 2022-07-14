
%==========================================================================
% text for rest after block in the cont RL paradigm
% nace.mikus@univie.ac.at
%==========================================================================
util_text(parm.ptb.scr.w,parm.ptb.scr.font,36,parm.ptb.scr.fontcol,1)
DrawFormattedText(parm.ptb.scr.w, 'Scanner Stopped!', 'center', 'center');
Screen('Flip',parm.ptb.scr.w)
WaitSecs(parm.exp.end_of_block_time);

Screen('FillRect', parm.ptb.scr.w, parm.ptb.scr.backgrd);
pos = parm.ptb.img.pos_fix;
Screen('FillOval', parm.ptb.scr.w, parm.ptb.scr.white, pos);
pos2 = pos;
pos2([1,3]) = pos2([1,3]) +60;
Screen('FillOval', parm.ptb.scr.w, parm.ptb.scr.white, pos2);
pos3 = pos;
pos3([1,3]) = pos3([1,3]) -60;
Screen('FillOval', parm.ptb.scr.w, parm.ptb.scr.white, pos3);
Screen('Flip',parm.ptb.scr.w)

WaitSecs(parm.exp.rest_time_length);
% 
% util_fixpoint(parm.ptb.scr.w,parm.ptb.scr.backgrd,parm.ptb.scr.white,parm.ptb.img.pos_fix)
% %         contRL_draw_outcome
%
%         Screen('FillRect', parm.ptb.scr.w, parm.ptb.scr.white, parm.ptb.img.slider);
%
%         Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.black, slider_response(3), response_line(2), slider_response(3), response_line(4),4);
%
% if logData == 1
%     log.times.startisitoout(curr.ct) = Screen('Flip',parm.ptb.scr.w);
%     log.all.events = [log.all.events, {'startisitoout'}];
%     log.all.onsets = [log.all.onsets, log.times.startisitoout(curr.ct)];
% else
%     ;
% end


%     image1 = parm.ptb.img.greenstim2.image;
% util_text(parm.ptb.scr.w,parm.ptb.scr.font,parm.ptb.scr.stimfont,parm.ptb.scr.white,1)
% 
% DrawFormattedText(parm.ptb.scr.w, resting_text, 'center', parm.ptb.img.pos_cue_text+55);
% Screen('Flip',parm.ptb.scr.w);
% 
% FlushEvents('keyDown'); resp = 0;
% 
% while resp == 0
%     
%     [keyIsDown, ~, keyCode] = KbCheck;
%     
%     if keyIsDown
%         
%         
%         resp  =1;
%         
%         resp  =1;
%         
%         
%     end
%     
%     WaitSecs(parm.exp.waitkbcheck)
%     
% end


% FlushEvents('keyDown');




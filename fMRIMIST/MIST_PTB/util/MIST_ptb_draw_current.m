
%==========================================================================
% draw the stimulus image in the center and the blank feedback response box
% nace.mikus@univie.ac.at
%==========================================================================

%% draw the number keypad

% Screen('FillRect', parm.ptb.scr.w, parm.ptb.scr.white, parm.ptb.img.slider )
util_text(parm.ptb.scr.w,parm.ptb.scr.font,parm.ptb.img.fontsize+20,parm.ptb.scr.blue,1)

k = response;
%     Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.backgrd,  parm.ptb.img.slider(1) + (k-1)*parm.ptb.img.box_size, parm.ptb.img.slider(2) , parm.ptb.img.slider(1) + (k-1)*parm.ptb.img.box_size,  parm.ptb.img.slider(4) ,parm.ptb.img.box_line_width);
% Screen('FillRect', parm.ptb.scr.w, parm.ptb.scr.white, parm.ptb.img.slider )    
DrawFormattedText(parm.ptb.scr.w, num2str(k-1), parm.ptb.img.slider(1) + (k-1)*parm.ptb.img.box_size + parm.ptb.img.box_size/2, parm.ptb.img.text_pos_y);




%% draw the equation

% 
% 
% Screen('Flip',parm.ptb.scr.w);
% clear image1; image1 = parm.ptb.img.greenstim.image;
% clear image2; 
% if stim_no == 0
% image2 = parm.ptb.img.QM.image;
% elseif stim_no ==1
% image2 = parm.ptb.img.S1.image;  
% elseif stim_no ==2
% image2 = parm.ptb.img.S2.image; 
% elseif stim_no ==3
% image2 = parm.ptb.img.S3.image; 
% end
%     
% clear texture1; texture1 = Screen('MakeTexture', parm.ptb.scr.w, image1);
% clear texture2; texture2 = Screen('MakeTexture', parm.ptb.scr.w, image2);
% 
% 
% Screen('DrawTextures',  parm.ptb.scr.w, texture1, [], parm.ptb.img.pos);
% Screen('DrawTextures',  parm.ptb.scr.w, texture2, [], parm.ptb.mine.pos);
% Screen('FillRect', parm.ptb.scr.w, parm.ptb.scr.white, parm.ptb.img.slider);
% % draw line 
% Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.red,  parm.ptb.img.slider(1), parm.ptb.img.slider(2)-parm.ptb.img.response_line_width/2, parm.ptb.img.slider(3),  parm.ptb.img.slider(2)-parm.ptb.img.response_line_width/2,parm.ptb.img.response_line_width);
% Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.grey2,  parm.ptb.img.slider(1)+ 1/3*parm.ptb.img.slide_length, parm.ptb.img.slider(2)-parm.ptb.img.response_line_width/2, parm.ptb.img.slider(3)- 1/3*parm.ptb.img.slide_length,  parm.ptb.img.slider(2)-parm.ptb.img.response_line_width/2,parm.ptb.img.response_line_width);
% Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.blue,  parm.ptb.img.slider(1)+ 2/3*parm.ptb.img.slide_length, parm.ptb.img.slider(2)-parm.ptb.img.response_line_width/2, parm.ptb.img.slider(3),  parm.ptb.img.slider(2)-parm.ptb.img.response_line_width/2,parm.ptb.img.response_line_width);
%   
% Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.red,  parm.ptb.img.slider(1), parm.ptb.img.slider(4)+parm.ptb.img.response_line_width/2, parm.ptb.img.slider(3),  parm.ptb.img.slider(4)+parm.ptb.img.response_line_width/2,parm.ptb.img.response_line_width);
% Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.grey2,  parm.ptb.img.slider(1)+ 1/3*parm.ptb.img.slide_length, parm.ptb.img.slider(4)+parm.ptb.img.response_line_width/2, parm.ptb.img.slider(3)- 1/3*parm.ptb.img.slide_length,  parm.ptb.img.slider(4)+parm.ptb.img.response_line_width/2,parm.ptb.img.response_line_width);
% Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.blue,  parm.ptb.img.slider(1)+ 2/3*parm.ptb.img.slide_length, parm.ptb.img.slider(4)+parm.ptb.img.response_line_width/2, parm.ptb.img.slider(3),  parm.ptb.img.slider(4)+parm.ptb.img.response_line_width/2,parm.ptb.img.response_line_width);
% 
% if confidence_reminder > 1
%      punish_text = 'Confidence rating!!!';
% 
%     util_text(parm.ptb.scr.w,parm.ptb.scr.font,parm.ptb.scr.stimfont,parm.ptb.scr.red,1)
% 
%     DrawFormattedText(parm.ptb.scr.w, punish_text, 'center', parm.ptb.img.slider(2) - 50);
% end



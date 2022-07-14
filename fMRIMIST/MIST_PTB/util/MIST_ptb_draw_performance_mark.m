
%==========================================================================
% draw the stimulus image in the center and the blank feedback response box
% nace.mikus@univie.ac.at
%==========================================================================


%% draw participant's performance mark vs the average:
% 
% avr correct answers should lie at 2/3s
avr_corr_ans = .72;


x_you = parm.ptb.img.performance_bar(1) +perc_corr*parm.ptb.img.performance_bar_length;
x_avr = parm.ptb.img.performance_bar(1) + avr_corr_ans*parm.ptb.img.performance_bar_length; %perc_corr_avg*parm.ptb.img.performance_bar_length;
util_text(parm.ptb.scr.w,parm.ptb.scr.font,30,parm.ptb.scr.black,1)


%Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.black,  x_you, parm.ptb.img.performance_bar(2), x_you ,   parm.ptb.img.performance_bar(4)+50,5);
DrawFormattedText(parm.ptb.scr.w, 'you', x_you+30, parm.ptb.img.performance_bar(4)+25);

%Write percentages to corners
DrawFormattedText(parm.ptb.scr.w, '0%', parm.ptb.img.performance_bar(1)-50, parm.ptb.img.performance_bar(4)-12.5);
DrawFormattedText(parm.ptb.scr.w, '100%', parm.ptb.img.performance_bar(1)+parm.ptb.img.performance_bar_length+10, parm.ptb.img.performance_bar(4)-12.5);


%Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.black,  x_avr, parm.ptb.img.performance_bar(2)-50, x_avr ,   parm.ptb.img.performance_bar(4),5);
DrawFormattedText(parm.ptb.scr.w, 'average', x_avr+30, parm.ptb.img.performance_bar(2)-10);


%draw triangles
%
% create a triangle of average
head   = [ x_avr, parm.ptb.img.performance_bar(2)-30 ]; % coordinates of head
width  = 30;           % width of arrow head
points = [ head-[width/1.5,0]         % left corner
    head+[width/1.5,0]         % right corner
    head+[0,width] ];      % vertex
Screen('FillPoly', parm.ptb.scr.w, parm.ptb.scr.black, points);

% create a triangle of 'you'
head2   = [ x_you, parm.ptb.img.performance_bar(4)+30 ]; % coordinates of head
width  = 30;           % width of arrow head
points2 = [ head2-[width/1.5,0]         % left corner
    head2+[width/1.5,0]         % right corner
    head2-[0,width] ];      % vertex
Screen('FillPoly', parm.ptb.scr.w, parm.ptb.scr.black, points2);



% log the trial data
if logData == 1
    
    
    log.exp.ct(curr.ct) = curr.ct;
    log.exp.block(curr.ct) = NaN;% curr.block;
    log.exp.trial(curr.ct) = NaN;% stimfile{find(strcmp(colidx,'trial'))}(curr.ct);
    log.exp.difficulty(curr.ct) = NaN;%curr.difd;
    % log.exp.stimset(curr.ct) = curr.set;
    %     log.exp.reward(curr.ct) = curr.rew;
    %     log.exp.mu(curr.ct) = curr.mu;
    %     log.exp.sd(curr.ct) = curr.sd;
    %     % log.exp.nonrew(curr.ct) = curr.non;
    % log.exp.pos1(curr.ct) = curr.pos1;
    % log.exp.pos2(curr.ct) = curr.pos2;
    log.exp.isi(curr.ct) = curr.isi;
    log.exp.isi2(curr.ct) = curr.isi2;
end
% ----------------------------------------
%(2) show symbols (selection,3s)
% ----------------------------------------
% define which stimulus to show

% PTB reference for accurate timing: http://peterscarfe.com/accuratetimingdemo.html
FlushEvents('keyDown');

% keep checking response for x seconds

curr.time = GetSecs;
% curr.resp = 0;
% curr.resp_final = NaN;
% curr.pos = 0;
% curr.rt = 0;
% curr.press = 0;


% define here once so that it can be copied

% slide_length= parm.ptb.img.slide_length;% = parm.ptb.img.slider(3) - parm.ptb.img.slider(1);
% response = 1;% of 100, also consider random
% slider_response = parm.ptb.img.slider;
%         slider_response(3) = slider_response(1) + response/slide_length;
timeline_length = parm.ptb.img.timeline(3) - parm.ptb.img.timeline(1);
timeline = parm.ptb.img.timeline;

% contRL_draw_stimuli %% maybe use??
startTime = now;
numberOfSecondsRemaining = curr.time2solve;
timeRemaining = curr.time2solve;
% curr.press = 0;
% firstpress = 1;
% holdkey = 0;
% response_final = NaN;
% confidence=NaN;
% response_line =  parm.ptb.img.line;
% try 
%     response = curr.resp;
% catch
%     
% end
response = randi([0 9]);

MIST_ptb_draw_equation
% MIST_ptb_draw_equation_window
if BlockType == 2 %show timeline and performance bar only in recording trials
    MIST_ptb_draw_performance_mark
    
    MIST_ptb_draw_timeline
end
MIST_ptb_draw_performance
MIST_ptb_draw_keypad_chosen

vbl = Screen('Flip',parm.ptb.scr.w);

if logData == 1
    log.times.starttrial(curr.ct) = vbl;
    log.all.events = [log.all.events, {'starttrial'}];
    log.all.onsets = [log.all.onsets, log.times.starttrial(curr.ct)];
end

respond_in_time = 0;
while timeRemaining > 0
    timeElapsed = (now - startTime) * 10 ^ 5;
    numberOfSecondsElapsed = round(timeElapsed);
    
    timeRemaining = curr.time2solve - timeElapsed;
    numberOfSecondsRemaining = curr.time2solve - numberOfSecondsElapsed;
    
    
    timeline(3) = timeline(1) + timeline_length* timeRemaining/curr.time2solve;
 
    timeline(3) = max( timeline(3),timeline(1)+1);
   
    % MIST_ptb_draw_keypad
    if BlockType == 2 %show timeline and performance bar only in recording trials
        MIST_ptb_draw_performance_mark
        
        MIST_ptb_draw_timeline
    end
    MIST_ptb_draw_performance
    MIST_ptb_draw_equation
%     MIST_ptb_draw_equation_window
    
    MIST_ptb_draw_keypad_chosen
    
    
    vbl = Screen('Flip',parm.ptb.scr.w);
    
    [ keyIsDown, ~, keyCode ] = KbCheck(-1);
    
    if keyIsDown
%         pressedkey = 1;
        %         if curr.press == 0
        %             curr.press = GetSecs;
        %         end
        if keyCode(parm.ptb.key.right)
            response = response + 1;
            if response == 10
                response =0;
            end
            
            %             if firstpress == 1
            %                 holdkey = 1; %1 for right
            %             end
            
        elseif keyCode(parm.ptb.key.left)
            response = response - 1;
            if response == -1
                response = 9;
            end
            
            %             if firstpress == 1
            %                 holdkey = 1; %1 for left
            %             end
        elseif keyCode(parm.ptb.key.escape)
            sca
        
        elseif keyCode(parm.ptb.key.confirm)
            %             response_final = response;
            respond_in_time = 1;
            if BlockType == 2 %show timeline and performance bar only in recording trials
                MIST_ptb_draw_performance_mark
                
                MIST_ptb_draw_timeline
            end
            MIST_ptb_draw_performance
            MIST_ptb_draw_equation
%             MIST_ptb_draw_equation_window
            
            MIST_ptb_draw_keypad_chosen
            
            if logData == 1
                log.times.startfinselection(curr.ct) = Screen('Flip',parm.ptb.scr.w);
                log.all.events = [log.all.events, {'startfinselection'}];
                log.all.onsets = [log.all.onsets, log.times.startfinselection(curr.ct)];
            else
                Screen('Flip',parm.ptb.scr.w);
            end
            %log.resp.btnstim(curr.ct) = curr.stim;
            %             Screen('DrawTextures',  parm.ptb.scr.w, texture1, [], parm.ptb.img.pos);
            %
            %             Screen('FillRect', parm.ptb.scr.w, parm.ptb.scr.white, parm.ptb.img.slider);
            %             Screen('FillRect', parm.ptb.scr.w, parm.ptb.scr.green, slider_response);
            %
            % go to the rating scale
            
            %             contRL_rating_scale
            %
            
            if logData == 1
                log.times.endfinselection(curr.ct) = GetSecs;
                log.all.events = [log.all.events, {'endfinselection'}];
                log.all.onsets = [log.all.onsets, log.times.endfinselection(curr.ct)];
                
                log.dur.finselection(curr.ct) = log.times.endfinselection(curr.ct) - log.times.startfinselection(curr.ct);
                
            end
            
            break
        end
        
        
        %     else
        %
        %         %         disp('key is not down')
        %         firstpress = 1;
        WaitSecs(0.1);
        KbReleaseWait;
    end
    % do small steps if first press after a pause otherwise move the
    % response line faster
    %     if holdkey == 1
    %         WaitSecs(0.1);
    %         firstpress = 0;
    %         holdkey = 0;
    %     else
    %         WaitSecs(0.001);
    %     end
    
    
end

curr.rt = numberOfSecondsElapsed;
% curr.resp            = response; % save the response in case there is no pick
if respond_in_time
    curr.resp            = response; % save the response in case there is no pick
curr.correct = response == result;
else
    curr.resp            = NaN; % save the response in case there is no pick
curr.correct = 0;   
end
correct_vect(T) = curr.correct;

rt_vect(T) = curr.rt;
correct_avg_vect(T) = rand(1)<0.7;
% curr.resp_final            = response_final;
% curr.confidence = confidence;

if logData == 1
    %     log.times.buttonpressfirst(curr.ct) = curr.press;
    log.resp.RTfirst(curr.ct) = curr.rt;
    log.resp.resp(curr.ct) = curr.resp;
    %     log.resp.final(curr.ct) = curr.resp_final;
    %     log.resp.confidence(curr.ct) = curr.confidence;
    log.times.endtrial(curr.ct) = GetSecs;
    
    log.all.events = [log.all.events, {'endtrial'}];
    log.all.onsets = [log.all.onsets, log.times.endtrial(curr.ct)];
    
    log.dur.trial(curr.ct) = log.times.endtrial(curr.ct) - log.times.starttrial(curr.ct);
end

% ----------------------------------------
% close the two textures to avoid memory overload
% ----------------------------------------

Screen('Close');

% ----------------------------------------
%(4) waiting for the feedback (2s)
% ----------------------------------------

util_fixpoint(parm.ptb.scr.w,parm.ptb.scr.backgrd,parm.ptb.scr.white,parm.ptb.img.pos_fix)
%         contRL_draw_outcome
%
%         Screen('FillRect', parm.ptb.scr.w, parm.ptb.scr.white, parm.ptb.img.slider);
%
%         Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.black, slider_response(3), response_line(2), slider_response(3), response_line(4),4);
%
if logData == 1
    log.times.startisitoout(curr.ct) = Screen('Flip',parm.ptb.scr.w);
    log.all.events = [log.all.events, {'startisitoout'}];
    log.all.onsets = [log.all.onsets, log.times.startisitoout(curr.ct)];
else
    Screen('Flip',parm.ptb.scr.w);
end
WaitSecs(curr.isi2);
%WaitSecs(3);
if logData == 1
    log.times.endisitoout(curr.ct) = GetSecs;
    log.all.events = [log.all.events, {'endisitoout'}];
    log.all.onsets = [log.all.onsets, log.times.endisitoout(curr.ct)];
    
    log.dur.isitoout(curr.ct) = log.times.endisitoout(curr.ct) - log.times.startisitoout(curr.ct);
end
% ----------------------------------------
%(5) show outcome (1s)
% ----------------------------------------
if BlockType == 2 %show timeline and performance bar only in recording trials
    MIST_ptb_draw_performance_mark
    
%     MIST_ptb_draw_timeline
end
MIST_ptb_draw_performance
%MIST_ptb_draw_equation
% MIST_ptb_draw_equation_window_outcome

%MIST_ptb_draw_keypad_chosen

MIST_ptb_draw_outcome
% % Screen('FillRect', parm.ptb.scr.w, parm.ptb.scr.white, parm.ptb.img.slider);
%
% Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.black, slider_feedback(3), response_line(2), slider_feedback(3), response_line(4),parm.ptb.img.response_line_width);
% Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.yellow, slider_feedback(3), response_line(2), slider_feedback(3), response_line(4),parm.ptb.img.response_line_width-2);
%
%Screen('FrameRect', parm.ptb.scr.w, parm.ptb.scr.red, slider_feedback, 1);

% response
% Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.black, slider_response(3), response_line(2), slider_response(3), response_line(4),parm.ptb.img.response_line_width);
% if draw_mean == 1
%     curr.mu;
%     slider_mean = min(slider_response(1) + curr.mu*slide_length*parm.exp.response_step,parm.ptb.img.slider(3));
%     Screen('DrawLine',parm.ptb.scr.w ,parm.ptb.scr.green, slider_mean, response_line(2), slider_mean, response_line(4),parm.ptb.img.response_line_width);
% end

if logData == 1
    log.times.startout(curr.ct) = Screen('Flip',parm.ptb.scr.w);
    log.all.events = [log.all.events, {'startout'}];
    log.all.onsets = [log.all.onsets, log.times.startout(curr.ct)];
else
    Screen('Flip',parm.ptb.scr.w);
end
WaitSecs(parm.exp.dur_outcome)
if logData == 1
    log.times.endout(curr.ct) = GetSecs;
    log.all.events = [log.all.events, {'endout'}];
    log.all.onsets = [log.all.onsets, log.times.endout(curr.ct)];
    
    %     log.resp.out(curr.ct) = curr.rew;
    %     log.resp.mu(curr.ct) = curr.mu;
    %     log.resp.sd(curr.ct) = curr.sd;
    log.dur.out(curr.ct) = log.times.endout(curr.ct) - log.times.startout(curr.ct);
end
% ----------------------------------------
% close the texture to avoid memory overload
% ----------------------------------------

Screen('Close');

% ----------------------------------------
%(6) ISI (3-7s, mean 5s)
% ----------------------------------------

util_fixpoint(parm.ptb.scr.w,parm.ptb.scr.backgrd,parm.ptb.scr.white,parm.ptb.img.pos_fix)
if logData == 1
    log.times.startiti(curr.ct) = Screen('Flip',parm.ptb.scr.w);
    log.all.events = [log.all.events, {'startiti'}];
    log.all.onsets = [log.all.onsets, log.times.startiti(curr.ct)];
else
    Screen('Flip',parm.ptb.scr.w);
end
WaitSecs(curr.isi);
if logData == 1
    log.times.enditi(curr.ct) = GetSecs;
    log.all.events = [log.all.events, {'enditi'}];
    log.all.onsets = [log.all.onsets, log.times.enditi(curr.ct)];
    
    log.dur.iti(curr.ct) = log.times.enditi(curr.ct) - log.times.startiti(curr.ct);
end

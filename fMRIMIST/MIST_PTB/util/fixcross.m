function [] = fixcross

% Display fixation cross.

global win rect FixCross

Screen('FillRect', win, 0, rect);
Screen('FillRect', win, [255,255,255], FixCross');
Screen('Flip', win);

end
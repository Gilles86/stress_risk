function checkerboard_fixcross

% Present checkerboard texture with fixation cross in place.

global win checks_texture FixCross

Screen('DrawTexture', win, checks_texture);

Screen('FillRect', win, [255,255,255], FixCross');

Screen('Flip', win);

end
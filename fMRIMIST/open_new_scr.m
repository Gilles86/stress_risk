function data = open_new_scr(data)

Screen('Preference', 'SkipSyncTests', data.PTB.skipsynctest);
HideCursor;

% Get Display Position and Resolution
% if ~data.flags.TESTING
    [w, rect] = Screen('OpenWindow', data.num_screen, data.PTB.colors.backcolor);%,screenRect, 32, ...
% else
%     perc = 0.5;%85;
%     [w, rect] = Screen('OpenWindow', data.num_screen, data.PTB.colors.backcolor, [0 0 2560 1600]*perc);%,screenRect, 32, ...
%     Screen('Preference','TextRenderer', 1)
% end

Screen('TextFont', w, data.PTB.font);
data.w = w;
data.wx = rect(3);
data.hx = rect(4) ; % ETH lab 1, otherwise 0.5
data.hx_full = rect(4);

HideCursor;

end
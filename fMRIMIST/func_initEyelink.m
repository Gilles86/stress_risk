function func_initEyelink(data,num_screen)

%initialize eyelink
%     status = Eyelink('initialize'); % ININITALIZE THE EYE TRACKER
Eyelink('initialize'); % ININITALIZE THE EYE TRACKER

% create screen
Screen('Preference', 'SkipSyncTests', data.PTB.skipsynctest);
%     [eye_screen, eye_Rect] = Screen('OpenWindow', 2, 0); %Screen('OpenWindow', num_screen, 0);
eye_screen = Screen('OpenWindow', num_screen, 0); %Screen('OpenWindow', num_screen, 0);
Screen('FillRect', eye_screen, 0);
Screen('Flip', eye_screen);

el = EyelinkInitDefaults(eye_screen); % default settings
EyelinkInit(0);
Screen('Flip', eye_screen);

Eyelink('Command', 'link_sample_data = LEFT,RIGHT,GAZE,AREA');
% %     EYELINK('openfile', 'demo.edf');
% %     Eyelink('closefile');
EyelinkDoTrackerSetup(el);

end
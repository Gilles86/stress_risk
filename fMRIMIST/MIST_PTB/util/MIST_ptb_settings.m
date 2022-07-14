% 
% %==========================================================================
% % settings for the MIST
% % nace.mikus@univie.ac.at
% %==========================================================================
% 
% % ----------------------------------------
% % some general things
% % ----------------------------------------
% 



parm.exp.startvol = 1;          % start at 7th MRI volume 
% 
parm.exp.countdown = 3;         % length of countdown if no MRI 
% 
if parm.info.MRI == true; parm.exp.countdown = parm.exp.startvol; end 
% 
parm.exp.ntrials = ntrials;%length(rewtraj);%max(stimfile{find(strcmp(colidx,'trial'))});
% 
% parm.exp.block = start_with_block;
% 
parm.exp.rest_time_length = rest_time_length; % 
%
parm.exp.block_time_length= block_time_length;
parm.exp.end_of_block_time = 2;
%
parm.exp.dur_isibegin = 1;      % fix dot at beginning is 3s
% 
parm.exp.dur_cue = 1;           % duration of cue is 3s
% 
parm.exp.performance_treshold = 0.4; % What should be correct on average? 
% parm.exp.dur_isicue = 1;        % isi before first trial is 2s
% 
% parm.exp.dur_trial = 20;         % duration of one trial is 5s
% 
% parm.exp.thickness = 5;         % line thickness selection 
% 
% parm.exp.response_step = 1/100;
% 
% parm.exp.waitkbcheck = 0.01;    % wait before KbCheck again 
% 
parm.exp.dur_selection = 0.3;   % show selection for 300ms
% 
% parm.exp.conf_rating_timing = 1.4;   % show selection for 300ms
% % parm.exp.dur_isiout = 1;        % isi before outcome is 1s
% 
parm.exp.dur_outcome = 2;       % duration outcome is 1s 
% 
% parm.exp.breaktime = 30;        % break for 30s block 1
% 
% if parm.info.subjID == 99; parm.exp.breaktime = 10; end %for training only 10 s
% 
% parm.exp.breakalert = 5;        % alert subject that next block starts in 5s
% 
parm.exp.dur_endscreen = 2;   % show end screen for 4s and then sca
% 
% %parm.exp.show_photos = includepictures;   % show scrambled and subj2 pictures?
% 
% parm.exp.show_arrow = true;     % show arrow for cue or pictures

% ----------------------------------------
% timestamp
% ----------------------------------------

time = fix(clock);
% 
parm.info.timestamp = [date,'_',num2str(time(end-2)),'_',num2str(time(end-1)),'_',num2str(time(end)),'h'];
% 
parm.info.nameLog = [parm.info.nameBase,'_',parm.info.paradigm,'_',parm.info.timestamp,'_log'];

% ----------------------------------------
% savename
% ----------------------------------------

savename = [parm.info.nameBase,'_',parm.info.timestamp];

saveTime2Solve = [parm.info.nameSubj,'_time2solve'];
% if break_after_block
%     savename = [parm.info.nameBase,'_Block_',num2str(start_with_block),'_',parm.info.timestamp];
% end
% % if break
% % ----------------------------------------
% % diary file 
% % ----------------------------------------
% 
% if diaryfile == true; diary(fullfile(parm.dirs.out,['diary_',savename,'.txt'])); end

% ----------------------------------------
% initialize output
% ----------------------------------------

clear log 

size = nan(500,1);

log.exp = struct(...
    'ct',size,...                       % current trial counter (over 2 blocks)
    'block',size,...                  % block
    'trial',size,...                    % trial within block
    'difficulty',size,...                % difficulty
    'isi',size,...              % isi / ITI between trials
    'isi2', size);                        % isi / ITI between trials
    
log.all = struct(...
    'events',cell(1,1),...              % all events in one, labels
    'onsets',[]);                       % all events in one, times
     
log.times = struct(...
    'mritrigger', nan(parm.exp.startvol,1),...                 
    'firstpulse',[],...                 % first MRI pulse, is last trigger
    'startexp',[],...                   % start time 
    'startcue',size,...                 % start of cue
    'startfix',size,...                 % fixation towards first trial
    'starttrial',size,...               % trial beginning 
    'startfinselection',size,...        % start of rating  
    'endfinselection',size,...          % end of rating  
    'endtrial',size,...                 % end of trial
    'startisitoout',size,...            % start isi to outcome screen
    'endisitoout',size,...
    'startout',size,...    
    'endout',size,...
    'startiti',size,...                 % start isi / ITI 
    'enditi',size,...          
    'startend',[],...                   % show end screen
    'endend',[]);
% % 
log.dur = struct(...
    'cue',size,...   
    'startfix',size,...
    'trial',size,...
    'finselection',size,...
    'isitoout',size,...
    'out',size,...
    'iti',size);
% %     
log.resp = struct(...
        'correct',size,...                  %  correct
    'solve_time',size,...                  %  time to solve
    'resp',size,...                     % response (save in case of no confirm)
    'RTfirst',size);                  % RT first button press
%     'RTfin',size,...                   % RT last selection
%     'confidence',size,...               % confidence (0 - 1.4)
%     'out',size                      % outcome error
% 
% ----------------------------------------
% keyboard settings
% ----------------------------------------

KbName('UnifyKeyNames');

if parm.info.MRI == false
    
    % input device is keyboard
    
    parm.ptb.key.input = 'keyboard';
    
    %check key codes using kbNameResult = KbName()
    %leave empty, press key, code is output
    
    parm.ptb.key.left = KbName('LeftArrow');
    parm.ptb.key.right = KbName('RightArrow');
    parm.ptb.key.confirm  = KbName('DownArrow');
    parm.ptb.key.escape = KbName('F10');
    
    parm.ptb.key.trigger = []; 
    
    queueKeyList = zeros(1, 256, 'double');
    queueKeyList(parm.ptb.key.left  ) = 1;
    queueKeyList(parm.ptb.key.right  ) = 1;
    queueKeyList(parm.ptb.key.confirm) = 1;
    deviceIndex=[];
else
    
    % we have a button box 
    
    parm.ptb.key.input = 'buttonbox';
    
    parm.ptb.key.left = KbName('4$'); %('1!');
    parm.ptb.key.right = KbName('2@');%('3#');
    parm.ptb.key.confirm = KbName('3#');%('2@');
    % important to keep KbName here because of it being a different coding
    
    parm.ptb.key.trigger = KbName('5%');%('6^');
   % parm.ptb.key.trigger = KbName('3#');
    parm.ptb.key.escape = KbName('tab');%KbName('F10');
    
    
    % restrict possible key presses to these
    % 32 / 49 / 50 / 51 = 4 buttonbox keys
    % 54 = 6 = scanner trigger 
%     
    queueKeyList = zeros(1, 256, 'double');
    queueKeyList(parm.ptb.key.left  ) = 1;
    queueKeyList(parm.ptb.key.right  ) = 1;
    queueKeyList(parm.ptb.key.confirm) = 1;
    %RestrictKeysForKbCheck([32,49,50,51,54]);
    keyboardIndices = GetKeyboardIndices();
    
    deviceIndex= [];
    
%     answer = input(['are you sure the device index is ', num2str(deviceIndex),' ?(y/n)'], 's');
%     if answer == 'n'
%         return
%     end
end
ListenChar(-1);
HideCursor;
% ----------------------------------------
% open screen
% info on screen/back-/frontbuffer etc.: 
% https://github.com/Psychtoolbox-3/Psychtoolbox-3/wiki/FAQ:-Textures,-Windows,-Screens
% https://github.com/Psychtoolbox-3/Psychtoolbox-3/wiki/FAQ:-Performance-Tuning
% ----------------------------------------

% close all existing 

sca

% get the nr of monitors
%SetResolution(1, 1280, 1024)
parm.ptb.scr.scrn = num_screen; %2 for Stimulus computer %max(Screen('Screens'));

% skip synctests

Screen('Preference', 'SkipSyncTests', parm.ptb.scr.skipsynctest);

% for scanner use screen 1, for office PC use parm.ptb.scr.scrn

%if parm.info.MRI == true; parm.ptb.scr.scrn = 1; else end 

% open screen 
%parm.ptb.scr.scrn = 1;
if camera == 1
    deltaX = 0;%750; % 750 % move to right/left
    deltaY = 0;%-1100; % move up by size of upper scr
    size_scr_x = 1920;
    size_scr_y = 1080;
    screenRect = [deltaX + 0, deltaY + 0, deltaX + size_scr_x*10/10, deltaY + size_scr_y*3/5];
    [parm.ptb.scr.w, parm.ptb.scr.rect] = Screen('OpenWindow', parm.ptb.scr.scrn, [], screenRect, [], [], [], [], []); %, kPsychGUIWindow);
    parm.ptb.scr.rect = parm.ptb.scr.rect .* .97; %resize used window to 95%
elseif camera == 0
    [parm.ptb.scr.w, parm.ptb.scr.rect] = Screen('OpenWindow', parm.ptb.scr.scrn);
end

%parm.ptb.scr.rect(3) = parm.ptb.scr.rect(3)/2;
% Query the frame duration (inter-frame-interval) / vertical refresh rate
% of monitor

parm.ptb.scr.ifi = Screen('GetFlipInterval', parm.ptb.scr.w);
HideCursor;
% Set the blend funciton for the screen

Screen('BlendFunction', parm.ptb.scr.w, 'GL_SRC_ALPHA', 'GL_ONE_MINUS_SRC_ALPHA');

% Numer of frames to wait before re-drawing
% Numer of frames to wait when specifying good timing. Note: the use of
% wait frames is to show a generalisable coding. For example, by using
% waitframes = 2 one would flip on every other frame. See the PTB
% documentation for details. In what follows we flip every frame.

parm.ptb.scr.waitframes = 1;

% verbosity level

% 0 - No output at all.
% 1 - Only severe error messages.
% 2 - Errors and warnings.
% 3 - Additional information, e.g., startup output when opening an onscreen window.
% 4 - Very verbose output, mostly useful for debugging PTB itself.
% 5 - Even more information and hints. Usually not what you want.

Screen('Preference', 'Verbosity', 3)

% Retreive the maximum priority number

topPriorityLevel = MaxPriority(parm.ptb.scr.w);

% This means PTB will take
% processing priority over other system and applicaiton processes. I
% normally do this before and after stimulus presentation, however, on
% modern multi-core processors keeping Priority on is unlikely to overload
% system resources. Plus, on Linux this operation can take much much longer
% then on Windows and OSX (up to minutes in some use cases). So it is now
% suggested that you set Priority once at the start of a script after
% setting up your onscreen window.

Priority(topPriorityLevel);

% hide cursor 
if hideCursor == 1;
 HideCursor;
end


% ----------------------------------------
% colors, background, text defaults
% ----------------------------------------

parm.ptb.scr.white = WhiteIndex(parm.ptb.scr.scrn);
parm.ptb.scr.black = BlackIndex(parm.ptb.scr.scrn);
parm.ptb.scr.grey = [125, 125, 125];
parm.ptb.scr.green = [0 255 0]; 
parm.ptb.scr.yellow = [255 255 0];
parm.ptb.scr.red = [255, 0, 0];
parm.ptb.scr.orange = [255,165,0];
parm.ptb.scr.blue = [0, 0, 255];
parm.ptb.scr.grey2 = [200, 200, 200];
parm.ptb.scr.grey3 = [100, 100, 100];
% background & text settings

parm.ptb.scr.backgrd = parm.ptb.scr.grey3;
parm.ptb.scr.fontcol = parm.ptb.scr.white;    
parm.ptb.scr.font = 'Arial';
parm.ptb.scr.fontsize = 35;

% font size in exp is bigger

parm.ptb.scr.stimfont = 52;

% % ----------------------------------------
% % load all images we need
% % ----------------------------------------
% 
% cd(parm.dirs.pics)
% 
% % if we show pictures of self/other
% 
% % if parm.exp.show_photos == true
%     
%     % self is always blurred
%     
% %     parm.ptb.img.self.filename = ['subj1_',parm.info.nameSubj,'_blurred.png'];
% %     
% %     parm.ptb.img.self.image = imread(parm.ptb.img.self.filename);
% %     
% %     % other is always sharp
% %     
% %     parm.ptb.img.other.filename = ['subj2_',char(parm.info.subj2ID),'.png'];
% %     
% %     parm.ptb.img.other.image = imread(parm.ptb.img.other.filename);
% %     
% % % end
% 
% % parm.ptb.img.arrow_self.filename = 'arrow_down_white.png';
% % 
% % parm.ptb.img.arrow_self.image = imread(parm.ptb.img.arrow_self.filename);
% % 
% % parm.ptb.img.arrow_other.filename = 'arrow_up_white.png';
% % 
% % parm.ptb.img.arrow_other.image = imread(parm.ptb.img.arrow_other.filename);
% % 
% % stimsets for both blocks within run 
% 
% % parm.ptb.img.setNrs = unique(stimfile{find(strcmp(colidx,'stimset'))})';
% 
% use_Stim = ssID;
% parm.ptb.img.QM.filename = 'GoldMineQM.png';
% parm.ptb.img.QM.image = imread(parm.ptb.img.QM.filename);
% 
% parm.ptb.img.S1.filename = 'GoldMineS1.png';
% parm.ptb.img.S1.image = imread(parm.ptb.img.S1.filename);
% 
% parm.ptb.img.S2.filename = 'GoldMineS2.png';
% parm.ptb.img.S2.image = imread(parm.ptb.img.S2.filename);
% 
% parm.ptb.img.S3.filename = 'GoldMineS3.png';
% parm.ptb.img.S3.image = imread(parm.ptb.img.S3.filename);
% 
% 
% % parm.ptb.img.QMtest.filename = 'subj2_Isabella.png';
% % parm.ptb.img.QMtest.image = imread(parm.ptb.img.QMtest.filename);
% 
% 
% % if practice == 1
% %     use_Stim = use_Stim +4;
% % end
% 
% parm.ptb.img.greenstim.filename = 'green_stim.png';
%  
% parm.ptb.img.greenstim.image = imread(parm.ptb.img.greenstim.filename);
% 
% parm.ptb.img.purplestim.filename = 'purple_stim.png';
%  
% parm.ptb.img.purplestim.image = imread(parm.ptb.img.purplestim.filename);
% 
% parm.ptb.img.greenstim2.filename = 'green_stim_angry.png';
%  
% parm.ptb.img.greenstim2.image = imread(parm.ptb.img.greenstim2.filename);
% 
% parm.ptb.img.purplestim2.filename = 'purple_stim_angry.png';
%  
% parm.ptb.img.purplestim2.image = imread(parm.ptb.img.purplestim2.filename);
% 
% % feedback images:
% 
% parm.ptb.img.neg_feedback.filename = 'neg.png';
% 
% parm.ptb.img.neg_feedback.image = imread(parm.ptb.img.neg_feedback.filename );
% 
% parm.ptb.img.pos_feedback.filename = 'pos.png';
% 
% parm.ptb.img.pos_feedback.image = imread(parm.ptb.img.pos_feedback.filename );
% 
% parm.ptb.img.null_feedback.filename = 'null.png';
% 
% parm.ptb.img.null_feedback.image = imread(parm.ptb.img.null_feedback.filename );
% 
% 
% 
% 
% 
% % cd symbols_white
% % 
% % 
% % parm.ptb.img.stimsets{1}.filename{1} = ['stimset_',num2str(use_Stim),'_pic_1.png'];
% % 
% % parm.ptb.img.stimsets{1}.image{1} = imread(parm.ptb.img.stimsets{1}.filename{1});
% % 
% % parm.ptb.img.stimsets{1}.filename{2} = ['stimset_',num2str(use_Stim),'_pic_2.png'];
% % 
% % parm.ptb.img.stimsets{1}.image{2} = imread(parm.ptb.img.stimsets{1}.filename{2});
% %     
% % 
% % 
% % cd ..
% % 
% % cd symbols_green
% % 
% % 
% % parm.ptb.img.selection{1}.filename{1} = ['stimset_',num2str(use_Stim),'_pic_1.png'];
% % 
% % parm.ptb.img.selection{1}.image{1} = imread(parm.ptb.img.selection{1}.filename{1});
% % 
% % parm.ptb.img.selection{1}.filename{2} = ['stimset_',num2str(use_Stim),'_pic_2.png'];
% % 
% % parm.ptb.img.selection{1}.image{2} = imread(parm.ptb.img.selection{1}.filename{2});
% % 
% % 
% % 
% % cd(parm.dirs.home)
% 
% % ----------------------------------------
% % image positions [x1 y1 x2 y2]
% % ----------------------------------------
% 
% parm.ptb.img.imgsize = [parm.ptb.scr.rect(3)/4 parm.ptb.scr.rect(3)*3/16];
% 
% parm.ptb.img.pos = [
%     (parm.ptb.scr.rect(3)/2 - parm.ptb.img.imgsize(1)/2)
%     (parm.ptb.scr.rect(4)/2 - parm.ptb.img.imgsize(2)/2)
%     (parm.ptb.scr.rect(3)/2 + parm.ptb.img.imgsize(1)/2)
%     (parm.ptb.scr.rect(4)/2 + parm.ptb.img.imgsize(2)/2)
%     ]';
% 
% parm.ptb.mine.pos = [
%     (parm.ptb.scr.rect(3)/2 - parm.ptb.img.imgsize(1)/2)
%     (parm.ptb.scr.rect(4)/4 - parm.ptb.img.imgsize(2)/2)
%     (parm.ptb.scr.rect(3)/2 + parm.ptb.img.imgsize(1)/2)
%     (parm.ptb.scr.rect(4)/4 + parm.ptb.img.imgsize(2)/2)
%     ]';
% 
% parm.ptb.feedback.pos = [
%     (parm.ptb.scr.rect(3)/2 - parm.ptb.img.imgsize(1)/2)
%     (parm.ptb.scr.rect(4)/2 - parm.ptb.img.imgsize(2)/2)
%     (parm.ptb.scr.rect(3)/2 + parm.ptb.img.imgsize(1)/2)
%     (parm.ptb.scr.rect(4)/2 + parm.ptb.img.imgsize(2)/2)
%     ]';
% 
% % parm.ptb.img.pos_right = [
% %     (parm.ptb.scr.rect(3)/4*3 - parm.ptb.img.imgsize(1)/2) left 
% %     (parm.ptb.scr.rect(4)/2 - parm.ptb.img.imgsize(2)/2) bottom
% %     (parm.ptb.scr.rect(3)/4*3 + parm.ptb.img.imgsize(1)/2) right
% %     (parm.ptb.scr.rect(4)/2 + parm.ptb.img.imgsize(2)/2) up
% %     ]'; left bottom right up
%  
% % % parm.ptb.img.pos_left_right = [
% %     parm.ptb.img.pos_left', parm.ptb.img.pos_right'
% %     ];
% parm.ptb.box = [2* parm.ptb.img.imgsize(1),  parm.ptb.img.imgsize(2)/2];
% 

% number dial
parm.ptb.img.slider = [parm.ptb.scr.rect(3)/5 
    3*parm.ptb.scr.rect(4)/4 
    4*parm.ptb.scr.rect(3)/5 
    3*parm.ptb.scr.rect(4)/4 + 100];
parm.ptb.img.slide_length = parm.ptb.img.slider(3) - parm.ptb.img.slider(1);
parm.ptb.img.box_size =  parm.ptb.img.slide_length/10;
parm.ptb.img.box_line_width = 7;
parm.ptb.img.fontsize = 60;
parm.ptb.img.text_pos_y = parm.ptb.img.slider(2) + (parm.ptb.img.slider(4)-parm.ptb.img.slider(2))*2/3;

%performance
% performance bar ratios
red_pos = 10*.45; % of 8
yellow_pos = 10*.55; % of 8
%green_ratio = 9; % of 8

parm.ptb.img.performance_bar = [parm.ptb.scr.rect(3)/10
    parm.ptb.scr.rect(4)/6;
    9*parm.ptb.scr.rect(3)/10
     parm.ptb.scr.rect(4)/6 + 50];
 
parm.ptb.img.performance_bar_length = 8/10*parm.ptb.scr.rect(3);
parm.ptb.img.performance_bar_red = [parm.ptb.scr.rect(3)/10
    parm.ptb.img.performance_bar(2)
    red_pos*parm.ptb.scr.rect(3)/10
    parm.ptb.img.performance_bar(4)];

parm.ptb.img.performance_bar_yellow = [red_pos*parm.ptb.scr.rect(3)/10
    parm.ptb.img.performance_bar(2)
    yellow_pos*parm.ptb.scr.rect(3)/10
    parm.ptb.img.performance_bar(4)];

parm.ptb.img.performance_bar_green = [yellow_pos*parm.ptb.scr.rect(3)/10
    parm.ptb.img.performance_bar(2)
    9*parm.ptb.scr.rect(3)/10
    parm.ptb.img.performance_bar(4)];

%equation
parm.ptb.img.equation_window = [parm.ptb.scr.rect(3)/5
    parm.ptb.scr.rect(4)/3
   4*parm.ptb.scr.rect(3)/5
    parm.ptb.scr.rect(4)/3 + 150 ];

% timeline
parm.ptb.img.timeline = [parm.ptb.scr.rect(3)/5
     parm.ptb.scr.rect(4)/3 + 170
    4*parm.ptb.scr.rect(3)/5
     parm.ptb.scr.rect(4)/3 + 200];
 
 %feedback window
%  parm.ptb.img.feedback = [parm.ptb.scr.rect(3)/5
%      parm.ptb.scr.rect(4)/3 + 300];
%     4*parm.ptb.scr.rect(3)/5
%      parm.ptb.scr.rect(4)/3 + 200];
% parm.ptb.img.line_pos =  parm.ptb.img.slider(1) + [1:9]*parm.ptb.img.box_size;
% parm.ptb.img.text_pos =  parm.ptb.img.slider(1) + [0:9]*parm.ptb.img.box_size + parm.ptb.img.box_size/2;
% parm.ptb.img.box_line_width
% parm.ptb.img.line = [0
%     3*parm.ptb.scr.rect(4)/4 - 25 
%     0
%     3*parm.ptb.scr.rect(4)/4 + 75];
% 
% % parm.ptb.img.confidencebox = [ 
% %     (parm.ptb.scr.rect(3)/2 + parm.ptb.img.imgsize(1)/2 + 100)
% %     (parm.ptb.scr.rect(4)/2 - parm.ptb.img.imgsize(2)/2)
% %      (parm.ptb.scr.rect(3)/2 + parm.ptb.img.imgsize(1)/2 + 200)
% %   (parm.ptb.scr.rect(4)/2 + parm.ptb.img.imgsize(2)/2)
% %    ]';
% % parm.ptb.img.textcertain = [
% %     (parm.ptb.scr.rect(3)/2 + parm.ptb.img.imgsize(1)/2 + 100)
% %     (parm.ptb.scr.rect(4)/2 - parm.ptb.img.imgsize(2)/2)
% %      (parm.ptb.scr.rect(3)/2 + parm.ptb.img.imgsize(1)/2 + 150)
% %   (parm.ptb.scr.rect(4)/2 + parm.ptb.img.imgsize(2)/2)
% %    ]';
% 
% % [
% %     (parm.ptb.scr.rect(3)/2 - parm.ptb.img.imgsize(1))
% %     (parm.ptb.img.imgsize(2)/4)
% %     (parm.ptb.scr.rect(3)/2 + parm.ptb.img.imgsize(1))
% %     (3*parm.ptb.img.imgsize(2)/4)
% %     ]';  left bottom right up
% parm.ptb.img.pos_cue_text = parm.ptb.scr.rect(4)/3 - 60; 
% 
% parm.ptb.img.pos_out_text = parm.ptb.scr.rect(4)/3*2 + 100; 
% 
% 
% parm.ptb.img.FeedbackRectWidthPixels = 6;
% 
% parm.ptb.img.response_line_width = 6;


% ----------------------------------------
% make fixation dot
% ----------------------------------------

parm.ptb.img.d = 14; % half diameter of fixation circle

parm.ptb.img.pos_fix = [
    (parm.ptb.scr.rect(3)/2 - parm.ptb.img.d) 
    (parm.ptb.scr.rect(4)/2 - parm.ptb.img.d) 
    (parm.ptb.scr.rect(3)/2 + parm.ptb.img.d) 
    (parm.ptb.scr.rect(4)/2 + parm.ptb.img.d)]';

% ----------------------------------------
%(-) basics
% ----------------------------------------

% text defaults
% util_text(screenWindow,TextFont,TextSize,TextColor,TextStyle) 
% TextStyle = 0=normal,1=bold,2=italic,4=underline,8=outline,32=condense,64=extend 
%cd ..
util_text(parm.ptb.scr.w,parm.ptb.scr.font,parm.ptb.scr.fontsize,parm.ptb.scr.fontcol,0)

Screen('FillRect', parm.ptb.scr.w, parm.ptb.scr.backgrd);

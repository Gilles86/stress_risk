function Risk_task_Wrapper(subjID,  RESTART )
%
% GOEKI'S SCRIPT!!!!
%
sessionID = 2;
% if nargin > 2, and RESTART = 1, then search for existing file and continue at run_start 

%% check input
if nargin < 2 | (RESTART == 0 & nargin == 2)
    RESTART = 0;
    data.run_start = 1;
    skip_FirstMIST = 0;
elseif nargin == 2 & RESTART == 1
 
    a = system(['cd C:\ExpFiles\Maike\stress_risk\experiment & C:\ExpFiles\Maike\virtualenv\risk\Scripts\python.exe ' [ 'C:\ExpFiles\Maike\stress_risk\experiment\make_trial_design.py ' sprintf('%02d', subjID) ' 1 1']]);
    data.run_start = 0;
    while ~(data.run_start > 1 & data.run_start <= 6)
        run_start = input('Restarting!!!\n At which run do you want to restart?');
        data.run_start = run_start;
    end 
    skip_FirstMIST = -1;
    while ~(skip_FirstMIST == 1 | skip_FirstMIST == 0)
        skip_FirstMIST = input('Restarting!!!\n Do you want to skip the first MIST after restart?(0/1)');
    end
end
data.RESTART = RESTART;

%% some inputs for the data collection
if data.RESTART == 0
    data.mri_experience = input('How often have you been scanned?');
    data.age = input('How old are you?');
    data.gender = input('Female/male? (f/m):', 's');
    data.first_name = input('Initial of first Name:', 's');
    data.last_name = input('Initial of last Name:', 's');
    data.condition = input('Condition? (0/1) : '); % Stress = 1 & Control = 0
    t_script_start = GetSecs;
    data.onsets.script_start = t_script_start;
end

%%

data.SUBID     = subjID; 
data.sessionID = sessionID;
data.numRUNS = 6; % # of RUNS!

%% get settings
[data,settings] = RISK_settings(data);
speedup_factor = data.speedup_factor;
F = data.flags;

%% MIST variables

if F.MIST == 1
    addpath(genpath([pwd, filesep,'MIST_PTB',filesep, 'util']));
end

%%

% create folders to save data and payments
data_folder    = fullfile(pwd, 'data', sprintf('SUBID_%04.f', data.SUBID),sprintf('sesh_%04.f', data.sessionID));
payment_folder = fullfile(pwd, 'payment');
temp_folder    = fullfile(pwd, 'temp');
if ~exist(strcat(data_folder), 'dir')
    mkdir(strcat(data_folder));
end
if ~exist(strcat(payment_folder), 'dir')
    mkdir(strcat(payment_folder));
end
if ~exist(strcat(temp_folder), 'dir')
    mkdir(strcat(temp_folder));
end
filename = sprintf('sess%04.f_subj%04.f_%s.mat', data.sessionID,data.SUBID,datestr(now, '_yy-mm-dd_HH-MM'));
data_file = fullfile(data_folder, filename);

% screen
if F.MRISCREEN
    num_screen = 1; % scanner
else
    num_screen = 0; %find_screen();
end

data.num_screen = num_screen;



%% if restart, load existing data
% adapt to take block number as input
if RESTART == 1
     
    data_file_load = strcat(data_folder,'/sess', num2str(sessionID,'%04.f'), '_subj', num2str(subjID,'%04.f'),'_*', '.mat');
    file2load = dir(data_file_load);
    try
        load(strcat(file2load(end).folder,'/',file2load(end).name),'data') % take last saved matfile
    catch
        error('Couldn''t load old subject file when trying to restart. Maybe file doesn''t exist yet?');
    end    
    data.run_start = run_start;
    data.RESTART = RESTART;
else
    data.run_start = 1;   
end

fprintf('\nsession ID: %i, subject ID: %i, condition: %i\n',sessionID,subjID,data.condition);
fprintf('\nRestart: %i\n',RESTART);

%% PTB (<- moved down from above eyelink)

% keyboard specs
KbName('UnifyKeyNames');
escapeKey = KbName('tab');
key_space = KbName('s'); %KbName('space');
key_trigger = KbName('5%'); % to be change to 5 for scanner
RestrictKeysForKbCheck([key_space, escapeKey, [KbName({'1!'; '2@'; '3#';'4$'})] , key_trigger ]);

ListenChar(-1);

% start
PsychDefaultSetup(1);
HideCursor;

Screen('Preference', 'SkipSyncTests', data.PTB.skipsynctest);

fontsizes = data.PTB.fontsizes;
colors = data.PTB.colors;
textcolor = colors.textcolor;

% dummy calls (to preload functions)
KbCheck(-1);
WaitSecs(0.001);
GetSecs;

% Set priority for script execution to realtime priority
%priorityLevel = MaxPriority(w);
%Priority(priorityLevel);


%% initialize variables

save(data_file,'data');


%% First saliva sample
if data.RESTART == 0
    sca
    data = open_new_scr(data);
    drawText(data.w, ['The experimenter will take the 2nd saliva sample now!'], textcolor, fontsizes.text, [data.wx 0 0 data.hx]);
    Screen(data.w, 'Flip');

    RestrictKeysForKbCheck(key_space);
    [~, keyCode]= KbPressWait(-1);
    keyCode = find(keyCode, 1);
    while keyCode ~= key_space
        WaitSecs(.005);
        [~, keyCode]= KbPressWait(-1);
        keyCode = find(keyCode, 1);
    end
    data.onsets.saliva(2) = datetime('now','Format','yyyy-MM-dd HH:mm:ss');
end

%% eyetracking calibration
if F.EYETRACKING == 1 && data.run_start == 1
    RestrictKeysForKbCheck([]);
    func_initEyelink(data,num_screen)
end
FlushEvents

%% ======================== START =========================== %

data.onsets.block_loop_start = GetSecs;

% iRUN is 1,3,5 unless run_start is not 1! Then, check where run_start is,
% to get back to odd integers: 1,3,5!

for iRUN = data.run_start:data.numRUNS
    % +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ %
    %                                 MIST 1                                     %
    % ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ %
    data.iRUN = iRUN;
    

    if F.MIST == 1 & skip_FirstMIST == 0
        % run MIST # 1
        data = func_MIST(data, key_space, escapeKey, key_trigger );
        w = data.w;
        sca
    end
    skip_FirstMIST = 0;
    save(data_file,'data');


    %% +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ %
    %                                EXPERIMENT                                    %
    % ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ %


    % HERE COMES GILLES' CODE
%     if F.EYETRACKING == 1
%         func_initEyelink(data,num_screen);
%     end
    % restrict keys before starting the other task
    RestrictKeysForKbCheck([]);
    ListenChar();
    sca
    if F.RISK_TASK == 1
        func_RISK(data.SUBID, data.iRUN, F.MAC);
    else
        data = open_new_scr(data);
        drawText(data.w, ['Risk task RUN ' num2str(iRUN) ], data.PTB.colors.textcolor, data.PTB.fontsizes.text);
        Screen(data.w, 'Flip');
        WaitSecs(4);
        sca
    end
    ListenChar(-1);
    save(data_file,'data');
    sca

end

%%
data.onsets.block_loop_end = GetSecs;




%% end of this part screen
data = open_new_scr(data);
drawText(data.w, 'End of the experiment!', textcolor, fontsizes.text, [data.wx 0 0 data.hx]);
Screen(data.w, 'Flip');

data.date = datetime('now','Format','yyyy-MM-dd HH:mm:ss');

%% compute final payment
data.score = 100; % GET THIS FROM THE RISK TASK
data.payment_bonus = ceil(( max(0,nansum(nansum(data.score)))) / data.game.exchange_rate);
data.payment_final = data.payment_bonus + data.game.show_up;

fprintf('\n\n\n+++ Subject done with task +++\n\nBonus =  %i\nTotal = %i\n\n',data.payment_bonus,data.payment_final);

%% save
% data
save(data_file,'data');

% payments
pay_file = strcat(payment_folder,'/sesh_', num2str(data.sessionID),'_sub_', num2str(data.SUBID) ,'.txt');
pay_T = table(data.SUBID,data.payment_bonus,data.payment_final, 'VariableNames',{'SubID','Bonus','Auszahlung'});
writetable(pay_T, pay_file ,'Delimiter','\t');

%% finish
% grey screen
WaitSecs(.5/speedup_factor);
text = instructions_texts(data.config.exp_language)

drawText(data.w, text.t1_scan, textcolor, fontsizes.text, [data.wx 0 0 data.hx]);
Screen(data.w, 'Flip');

RestrictKeysForKbCheck(key_space);
[~, keyCode]= KbPressWait(-1);
keyCode = find(keyCode, 1);
while keyCode ~= key_space
    WaitSecs(.005);
    [~, keyCode]= KbPressWait(-1);
    keyCode = find(keyCode, 1);
end

% last questionaire

drawText(data.w, ['The experimenter will take the 5th saliva sample now!'], textcolor, fontsizes.text, [data.wx 0 0 data.hx]);
Screen(data.w, 'Flip');

RestrictKeysForKbCheck(key_space);
[~, keyCode]= KbPressWait(-1);
keyCode = find(keyCode, 1);
while keyCode ~= key_space
    WaitSecs(.005);
    [~, keyCode]= KbPressWait(-1);
    keyCode = find(keyCode, 1);
end

data.onsets.saliva(5) = datetime('now','Format','yyyy-MM-dd HH:mm:ss');
data.onsets.VAS(6) = GetSecs;
data.questionaire_ans(:,6) = questionaire( data);
Screen(w, 'Flip');

save(data_file,'data');

drawText(data.w, text.exp_end, textcolor, fontsizes.text, [data.wx 0 0 data.hx]);
Screen(data.w, 'Flip');

% close & clean-up
RestrictKeysForKbCheck(key_space);
[~, keyCode]= KbPressWait(-1);
keyCode = find(keyCode, 1);
while keyCode ~= key_space
    WaitSecs(.005);
    [~, keyCode]= KbPressWait(-1);
    keyCode = find(keyCode, 1);
end

save(data_file,'data');
sca
RestrictKeysForKbCheck([]);
func_payment_calc(data.SUBID,data.sessionID);

%drawText(data.w, 'Bye...', textcolor, fontsizes.text);
%Screen(data.w, 'Flip');
WaitSecs(2/speedup_factor);

save(data_file,'data');

sca;
ShowCursor;
fclose('all');
Priority(0);
ListenChar();



end

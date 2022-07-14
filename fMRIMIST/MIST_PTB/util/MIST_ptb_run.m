function MIST_ptb_run(subjID, blockID, BlockType, num_screen, block_time_length)

%==========================================================================
% function run_reward(subjID,blockID,groupID)
%
% This is the main code that runs the reinforcement-learning task.
% It will save data to the 'logfiles' subfolder. This code uses the
% PsychToolbox software (psychtoolbox.org):
%
% subjID:   *number* between 1 and 80, for training 99
% blockID:     *number* 1 to 4
% groupID:    *number* 1 or 2 (1 = sensitized group, 2 = test/retest)
% For training, use subjID 99, groupID = 1, blockID = 1 or 2
%
%

% Nace Mikus
% (adapted from Isabella Wagner)
% University of Vienna
%
%
% version 10-04-2019
%==========================================================================

%%
% clearvars
close all
clc
%% defaults:
MRI_mode = 1;
name_prefix = 'MIST'; % 'Test_retest_sub';
ntrials = 100; % 40 (8 per block * 5 + 2*2 ISI);
no_of_blocks = 1;
block_time_length = block_time_length; %seconds / put to very high if we want to use trial numbers instead
rest_time_length = .1; %seconds
% Trials_in_block > trials_block
ntrials_per_block = ntrials/no_of_blocks;

camera = 1 ; % '1 for Microsoft Camera' and '2 for Matlab Camera' and '0 for no camera' 
diff_stress = 2 ; % '0' for all 4 level, '1' for 3 highest levels, '2' for 2 highest level and '3' for highest level only

debug = 0; %clear functions
save_time2solve = 1;
% skip_instructions = 0;
% short_instructions_debug = 0; % keep instructions short for debugging purposes
check_save = 0; % make runs super short to see if it saves data.

break_after_block = 0; % eg for the mist;
hideCursor = 0;

if debug == 1
    PsychDebugWindowConfiguration(0,0.5)
    
end

subjID = subjID;%input('Sub ID? ');
blockID = blockID;%input('Block?');
practice = 0;%input('Practice Session? (0/1):');
BlockType = BlockType ;% input('Time limits, recording session? (0/1) : ');
BlockType = BlockType +1; % 2 stress, 1 no stress

rng('shuffle');

% ----------------------------------------
% paths
% ----------------------------------------

parm.info.paradigm = 'MIST_ptb';
parm.info.prefix = name_prefix;
MIST_ptb_paths; % set paths - still change if need be


if practice
    ntrials = 5;
    MRI_mode = 0;
    save_time2solve = 1;
end
if ~exist([parm.dirs.time '/MIST_Sub', num2str(subjID),'_time2solve.mat']);
    %input('time2solve does not exist for the participant, using default options (ENTER to continue)');
    disp('time2solve does not exist for the participant, using default options!!!')
    time2solveMatrix = [6;6;6;7];%[5;6;7;10];
else
    load([parm.dirs.time '/MIST_Sub', num2str(subjID),'_time2solve.mat'])
    
end
% 
% start_with_block = 1;
% if break_after_block
%     start_with_block = input('Which Block is it now?');
% end


%==========================================================================
%% warnings
%--------------------------------------------------------------------------
if BlockType == 1
    disp(['Not recording session.']);
    %name_prefix = 'MIST_ptb_NotRecording';
else
    disp(['Recording session!!']);
    %name_prefix = 'MIST_ptb_VeryMuchRecording';
end
if save_time2solve == 1
    disp('saving time to solve');
    
end

if debug == 1
    disp('Debug Mode!!');
end

if MRI_mode
    disp('Scanner mode');
end

%input('Press ENTER to continue');

%==========================================================================
%% A.    Getting started.
%--------------------------------------------------------------------------

parm.info.subjID = subjID;
parm.info.BlockType = BlockType;
parm.info.blockID = blockID;

% parm.info.groupID = groupID;
%parm.info.subj2ID = subj2ID;





if subjID < 10; parm.info.nameSubj = [parm.info.prefix,'_Sub0',num2str(subjID)]; else parm.info.nameSubj = [parm.info.prefix,'_Sub',num2str(subjID)]; end
if BlockType == 1
    BlockTypeName = 'Rec';
else
    BlockTypeName = 'NoRec';
end
parm.info.nameBase = [parm.info.nameSubj,'_',BlockTypeName, '_Block',num2str(blockID)];


% ----------------------------------------
% environment MRI? (true or false)
% ----------------------------------------

parm.info.MRI = MRI_mode;

% ----------------------------------------
% skip sync test? (1 = yes, 0 = no)
% ----------------------------------------

parm.ptb.scr.skipsynctest = 1;

% ----------------------------------------
% diary? (true or false)
% ----------------------------------------

diaryfile = false;

% ----------------------------------------
% write text file? (true or false)
% ----------------------------------------

%textfile = true;


% ----------------------------------------
% stimulus file
% ----------------------------------------


colidx{1} = 'ct';           % 1 = continuous trial counter
colidx{2} = 'session';      % 2 = session? which session
colidx{3} = 'run';          % 3 = run ?? not sure yet what for
colidx{4} = 'block';        % 4 = block
colidx{5} = 'trial';        % 5 = trial
colidx{6} = 'reward';       % 6 = reward
colidx{7} = 'mu';           % 7 = mu of stimulus
colidx{8} = 'sd';           % 8 = sd of stimulus (1/2)
colidx{9} = 'isi';          % 9 = ISI duration (3-7s in steps of 500ms)
colidx{10} = 'isi2';        % 10 = ISI2 duration (3-7s in steps of 500ms)
% colidx{11} = 'pos2';        % 11 = stimulus two position (1/2)
% colidx{14} = 'isi';         % 14 = ISI duration (3-7s in steps of 500ms)
% colidx{15} = 'isi2';        % 14 = ISI2 duration (3-7s in steps of 500ms)
% clear fileID; fileID = fopen(fullfile(parm.dirs.stimfile,parm.info.stimfile),'r');
% clear formatSpec; formatSpec = '%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f';
% clear stimfile; stimfile = textscan(fileID, formatSpec,'headerlines',1,'delimiter','\t');
% fclose all;


% ----------------------------------------
% define rew traj
% ----------------------------------------
%
% if exist('stimfiles/stim.mat', 'file')
%     if blockID == 1
%         load('stimfiles/stim_ses1.mat');
%     elseif blockID == 2
%         load('stimfiles/stim_ses2.mat');
%     end
% else
%     input('Cannot find stim file, creating my own. Press ENTER to continue.');
%     def_rew
%
% end
% if check_save
%     stim.rew_traj_set = stim.rew_traj_set(1:4);
%     stim.mu_traj_set= stim.mu_traj_set(1:4);
%     stim.sd_traj_set= stim.sd_traj_set(1:4);
% end

% ----------------------------------------
% define rew traj practice
% ----------------------------------------
%
% if exist('stimfiles/stim_prac.mat', 'file')
%
%     load('stimfiles/stim_prac.mat')
% else
%     def_rew_prac
% end
%
% if short_instructions_debug
%     blocks =  max(stimfile_practice(:,2));
%     stimfile_practice = [repmat(1,[blocks,1]), [1:blocks]', repmat(1,[blocks,1])];
% end
% load provisory stimfile
%
% rewtraj = stim.rew_traj_set;%randn(30,1)*10 + 50;
% mutraj = stim.mu_traj_set;
% sdtraj  = stim.sd_traj_set;
% block_size = round(length(rewtraj)/no_of_blocks);


% ------------------------------------------------------------------
% if set the starting trial to match the starting block
% ------------------------------------------------------------------

% adjust ct, block, trial counters if necessary
% check last logfile, at which trial task stopped

startct = 1;% (start_with_block-1)*block_size+1;

%startblock = 1;

starttrial = 1;%(start_with_block-1)*block_size+1;
% ----------------------------------------
% settings
% ----------------------------------------

% allocate data storage,
% load all images,
% set PTB parameters
% show first instructions,

%MIST_ptb_settings;
MIST_ptb_settings;


%==========================================================================
%% B.  Starting scanner
%--------------------------------------------------------------------------

% ----------------------------------------
% 'waiting for scanner ... '
% ----------------------------------------

if parm.info.MRI == true; util_draw_waitmri(parm.ptb.scr.w); end

% ----------------------------------------
% count down / waiting for scanner
% ----------------------------------------

[trigger_onsets] = util_countdown(parm.info.MRI,parm.exp.countdown,parm.ptb.scr.w,parm.ptb.key.trigger);
%[trigger_onsets] = util_countdownKbQueue(parm.info.MRI,parm.exp.countdown,parm.ptb.scr.w,parm.ptb.key.trigger);



if parm.info.MRI == true
    
    log.times.mritrigger = trigger_onsets;
    
    log.times.firstpulse = log.times.mritrigger(end);
    
end

%==========================================================================
%% C.    Loop over all blocks / trials
%--------------------------------------------------------------------------



try
    
    %start diary
    
    if diaryfile == true; diary on; end
    
    fprintf('start with trial loop. \n');
    
    % log data
    logData = 1; %log Data
    %     stim_no = 0; %set the mine to be QM
    %
    %     draw_mean = 0;
    %
    % ----------------------------------------
    % draw fixation dot = start_exp
    % ----------------------------------------
    
    % util_fixpoint(parm.ptb.scr.w,parm.ptb.scr.backgrd,parm.ptb.scr.white,parm.ptb.img.pos_fix)
    
    log.times.startexp = Screen('Flip',parm.ptb.scr.w);
    log.all.events = [log.all.events, {'startexp'}];
    log.all.onsets = [log.all.onsets, log.times.startexp];
    
    %     WaitSecs(parm.exp.dur_isibegin);
    
    % ----------------------------------------
    % start the run
    % ----------------------------------------
    
    % continuous trial counter
    
    curr.ct = startct;
    
    
    
    
    
    log.times.startcue(curr.ct) = Screen('Flip',parm.ptb.scr.w);
    log.all.events = [log.all.events, {'startcue'}];
    log.all.onsets = [log.all.onsets, log.times.startcue(curr.ct)];
    
    WaitSecs(parm.exp.dur_cue);
    
    log.dur.cue(curr.ct) = GetSecs - log.times.startcue(curr.ct);
    
    % clear memory
    
    Screen('Close')
    
    %     ----------------------------------------
    %     fixation cross (2s)
    %     ----------------------------------------
    
    util_fixpoint(parm.ptb.scr.w,parm.ptb.scr.backgrd,parm.ptb.scr.white,parm.ptb.img.pos_fix)
    
    log.times.startfix(curr.ct) = Screen('Flip',parm.ptb.scr.w);
    log.all.events = [log.all.events, {'startfix'}];
    log.all.onsets = [log.all.onsets, log.times.startfix(curr.ct)];
    
    %     WaitSecs(parm.exp.dur_isicue);
    
    log.dur.startfix(curr.ct) = GetSecs - log.times.startfix(curr.ct);
    
    % ----------------------------------------
    % start the block
    % ----------------------------------------
    %     block_trial = 0;
    %     confidence_reminder = 0;
    
    correct_vect = NaN(parm.exp.ntrials,1);
    correct_avg_vect = NaN(parm.exp.ntrials,1);
    difficulty_vect =  NaN(parm.exp.ntrials,1);
    rt_vect=  NaN(parm.exp.ntrials,1);
    difficulty_trial_scheme=[];
    for k =  1 : round(parm.exp.ntrials/4)
        difficulty_trial_scheme = [difficulty_trial_scheme, min(ones(1,4).*4,(randperm(4)+ diff_stress )) ];% randperm(4) ]; 
    end
    if BlockType == 1
        time2solve = 60*ones(1,4);
    elseif BlockType == 2
        time2solve = time2solveMatrix;
    end
    
    perc_corr =1;
    perc_corr_avg = 1;
    
    BlockTimePassed = 0;
    BlockStartTime = GetSecs;
    blockno = 0;
    Trials_in_block=0;
    for T = starttrial: parm.exp.ntrials
        BlockTimePassed = GetSecs - BlockStartTime;
        Trials_in_block = Trials_in_block +1;
        %% determine the equation
        if  or(BlockTimePassed > block_time_length, Trials_in_block > ntrials_per_block );
            blockno = blockno +1;
            
            MIST_resting_screen;
            if blockno == no_of_blocks
                break
            end
            BlockStartTime = GetSecs;
            Trials_in_block = 0;
        end
        difficulty_vect(T) =  difficulty_trial_scheme(T);% randi(4);
        if  difficulty_vect(T) == 1
            eq_length =3;
            op_length = 2;
        elseif  difficulty_vect(T) == 2
            eq_length =3;
            op_length = 3;
        elseif  difficulty_vect(T) == 3
            eq_length =4;
            op_length = 4;
        else
            eq_length =5;
            op_length = 4;
        end
        
        get_math_equations
        
        %% determine the performance
%         perc_corr_defficulty = NaN(4,1);
%         for k = 1 : 4
%             perc_corr_defficulty(k) = sum(correct_vect(difficulty_vect==k))/length(correct_vect(difficulty_vect==k));
%             
%             %adjust the time2solve if recording
%             if BlockType == 2
%                 if perc_corr_defficulty(k) > parm.exp.performance_treshold
%                     time2solve(k) = 0.8*time2solve(k);
%                 else
%                     time2solve(k) = min(8, 1.2*time2solve(k));
%                 end
%             end
%         end

        perc_corr_defficulty = rmmissing(correct_vect);
        perc_corr_defficulty = mean(perc_corr_defficulty(max(1,end-0):end));
        
            %adjust the time2solve if recording
            if BlockType == 2
                if perc_corr_defficulty > parm.exp.performance_treshold
                    time2solve = 0.8*time2solve;
                else
                    time2solve = min(8, 1.1*time2solve);
                end
            end
        
        
        
        
        %% determine the time to solve the quation
        
        curr.time2solve = time2solve(difficulty_vect(T))
        % position stimiulus 2
        if MRI_mode
            curr.isi = max(round(gamrnd(.5,1),1),0); %(randi(20)-10)/10 +2;% 2000 +- 500 ms; stimfile{find(strcmp(colidx,'isi'))}(curr.ct)/1000;           % isi
            curr.isi2 = round(rand, 1)/2; %(randi(20)-10)/10 +2;%(randi(10)-5)/10 +2;%stimfile{find(strcmp(colidx,'isi2'))}(curr.ct)/1000;           % isi
        else
            curr.isi = .1; %(randi(20)-10)/10 +2; % 2000 +- 500 ms; stimfile{find(strcmp(colidx,'isi'))}(curr.ct)/1000;           % isi
            curr.isi2 = .1 ; %(randi(20)-10)/10 +2;%(randi(10)-5)/10 +2;%stimfile{find(strcmp(colidx,'isi2'))}(curr.ct)/1000;           % isi
         
        end
        
        % run the trial
        MIST_ptb_trial
        
        perc_corr = nansum(correct_vect)/sum(~isnan(correct_vect));
        disp(['perentage correct = ', num2str(perc_corr)]);
        perc_corr_avg =nansum(correct_avg_vect)/sum(~isnan(correct_avg_vect));
        disp(['avrg correct = ', num2str(perc_corr_avg)]);
        % ----------------------------------------
        % ct counter
        % ----------------------------------------
        
        curr.ct = curr.ct + 1;
    end
    %     ----------------------------------------
    %     save times
    %     ----------------------------------------
    if save_time2solve == 1
        
        time2solveMatrix =[mean(rt_vect(difficulty_vect==1));...
            mean(rt_vect(difficulty_vect==2));...
            mean(rt_vect(difficulty_vect==3));...
            mean(rt_vect(difficulty_vect==4))];
        
        save(fullfile(parm.dirs.time,[saveTime2Solve,'.mat']), 'time2solveMatrix');
    end
    
    fprintf('done with trial loop. \n');
    
    % ----------------------------------------
    % show end screen
    % ----------------------------------------
    
    util_text(parm.ptb.scr.w,parm.ptb.scr.font,36,parm.ptb.scr.fontcol,1)
    
    util_draw_end(parm.ptb.scr.w)
    
    log.times.startend(1) = Screen('Flip',parm.ptb.scr.w);
    
    WaitSecs(parm.exp.dur_endscreen);
    
    log.times.endend(1) = GetSecs;
    
    % ----------------------------------------
    % close PTB
    % ----------------------------------------
    
    util_closeptb
    
    % ----------------------------------------
    % save
    % ----------------------------------------
    
    reward_save;
    
    
    % ----------------------------------------
    % write tab-delimited text log file
    % ----------------------------------------
    
    %      reward_txtfile
    
    % ----------------------------------------
    % end diary
    % ----------------------------------------
    
    if diaryfile == true; diary off; end
    
    %     points  = sum(100- abs(log.resp.out -log.resp.final) );
    %     moneyz  = 0;%4*sum(log.resp.out==1)/100;
    fprintf('saved and closed all')
    disp(' ')
    %
    %     fprintf(['The participant earned ', num2str(points), ' points,'])
    %     disp(' ')
    %     fprintf(['which is ', num2str(moneyz), ' euros,'])
    %     disp(' ')
    
catch err
    
    % ----------------------------------------
    % catch error and save
    % ----------------------------------------
    
    rethrow(err);
    
    psychrethrow(psychlasterror);
    
    savename = [savename,'_err'];
    
    util_closeptb
    
    reward_save
    
    if diaryfile == true; diary off; end
    
end

%==========================================================================
% end
%--------------------------------------------------------------------------

%%cd ..



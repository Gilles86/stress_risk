function data = func_MIST(data, key_space, escapeKey, key_trigger  )

%% check for iRUN

if ~isfield(data,'iRUN')
    iRUN = 1;
else
    iRUN = data.iRUN;
end

RestrictKeysForKbCheck([key_space, escapeKey, [KbName({'1!'; '2@'; '3#';'4$'})] , key_trigger ]);

%% MIST at the very beginning

if  iRUN == 1

    % run questionaire before Mist
    sca
    data = open_new_scr(data);
    data.onsets.VAS(2) = GetSecs;
    data.questionaire_ans(:,2) = questionaire(data);
    Screen(data.w, 'Flip');

    sca
    % start with Math Trials
    %First Part
    RestrictKeysForKbCheck([key_space, escapeKey, [KbName({'1!'; '2@'; '3#';'4$'})] , key_trigger ]);
    data.onsets.MIST(1) = GetSecs;
    MIST_ptb_run(data.SUBID, 1, data.condition, data.num_screen, 175/data.speedup_factor); % %MIST_ptb_run(subjID, blockID, BlockType, block_time_length)

    RestrictKeysForKbCheck([key_space]);
    %wait for tab
    [timeSecs, keyCode]= KbPressWait(-1); %startSecs+3);
    keyCode = find(keyCode, 1);
    while keyCode ~= key_space
        WaitSecs(.005);
        [timeSecs, keyCode]= KbPressWait(-1); %startSecs+3);
        keyCode = find(keyCode, 1);
    end

    sca

    RestrictKeysForKbCheck([key_space, escapeKey, [KbName({'1!'; '2@'; '3#';'4$'})] , key_trigger ]);
    %Second Part
    MIST_ptb_run(data.SUBID, 2, data.condition,data.num_screen, 117/data.speedup_factor);

    RestrictKeysForKbCheck([key_space]);
    %wait for tab
    [timeSecs, keyCode]= KbPressWait(-1); %startSecs+3);
    keyCode = find(keyCode, 1);
    while keyCode ~= key_space
        WaitSecs(.005);
        [timeSecs, keyCode]= KbPressWait(-1); %startSecs+3);
        keyCode = find(keyCode, 1);
    end

    sca
    data = open_new_scr(data);
    %questionaire
    data.onsets.VAS(3) = GetSecs;
    data.questionaire_ans(:,3) = questionaire(data);
    Screen(data.w, 'Flip');

end

%% MIST after block 2 run the MIST again

if iRUN == 3 || iRUN == 5


    sca
    %First Part
    RestrictKeysForKbCheck([key_space, escapeKey, [KbName({'1!'; '2@'; '3#';'4$'})] , key_trigger ]);

    MIST_ptb_run(data.SUBID, 3, data.condition, data.num_screen, 172/data.speedup_factor); % %MIST_ptb_run(subjID, blockID, BlockType, block_time_length)
    RestrictKeysForKbCheck([key_space]);
    %wait for tab
    [timeSecs, keyCode]= KbPressWait(-1); %startSecs+3);
    keyCode = find(keyCode, 1);
    while keyCode ~= key_space
        WaitSecs(.005);
        [timeSecs, keyCode]= KbPressWait(-1); %startSecs+3);
        keyCode = find(keyCode, 1);
    end
    sca
    RestrictKeysForKbCheck([key_space, escapeKey, [KbName({'1!'; '2@'; '3#';'4$'})] , key_trigger ]);

    %Second Part
    MIST_ptb_run(data.SUBID, 4, data.condition, data.num_screen, 114/data.speedup_factor);

    RestrictKeysForKbCheck([key_space]);
    %wait for tab
    [timeSecs, keyCode]= KbPressWait(-1); %startSecs+3);
    keyCode = find(keyCode, 1);
    while keyCode ~= key_space
        WaitSecs(.005);
        [timeSecs, keyCode]= KbPressWait(-1); %startSecs+3);
        keyCode = find(keyCode, 1);
    end

    sca

    data = open_new_scr(data);

    if iRUN == 3
        data.onsets.MIST(2) = GetSecs;
        data.onsets.saliva(3) = datetime('now','Format','yyyy-MM-dd HH:mm:ss');

        drawText(data.w, ['The experimenter will take the 3rd saliva sample now!'], data.PTB.colors.textcolor, data.PTB.fontsizes.text, [data.wx 0 0 data.hx]);
        Screen(data.w, 'Flip');

        RestrictKeysForKbCheck(key_space);
        [~, keyCode]= KbPressWait(-1);
        keyCode = find(keyCode, 1);
        while keyCode ~= key_space
            WaitSecs(.005);
            [~, keyCode]= KbPressWait(-1);
            keyCode = find(keyCode, 1);
        end

        data.onsets.VAS(4) = GetSecs;
        data.questionaire_ans(:,4) = questionaire(data);
        Screen(data.w, 'Flip');
    elseif iRUN == 5
        data.onsets.MIST(3) = GetSecs;
        data.onsets.saliva(4) = datetime('now','Format','yyyy-MM-dd HH:mm:ss');

        drawText(data.w, ['The experimenter will take the 4th saliva sample now!'], data.PTB.colors.textcolor, data.PTB.fontsizes.text, [data.wx 0 0 data.hx]);
        Screen(data.w, 'Flip');

        RestrictKeysForKbCheck(key_space);
        [~, keyCode]= KbPressWait(-1);
        keyCode = find(keyCode, 1);
        while keyCode ~= key_space
            WaitSecs(.005);
            [~, keyCode]= KbPressWait(-1);
            keyCode = find(keyCode, 1);
        end

        data.onsets.VAS(5) = GetSecs;
        data.questionaire_ans(:,5) = questionaire(data);
        Screen(data.w, 'Flip');
    end


end

RestrictKeysForKbCheck([key_space, escapeKey, [KbName({'1!'; '2@'; '3#';'4$'})] , key_trigger ]);
FlushEvents

end
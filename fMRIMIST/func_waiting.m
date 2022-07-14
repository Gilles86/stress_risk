function func_waiting(AUTOMATIC_PROGRESS , temp_folder, subjID, iBlock,key_block_start)

if isempty(iBlock) 
    
    if AUTOMATIC_PROGRESS == 1
        while numel(dir([temp_folder '/EXP_START.txt'])) < 1
            WaitSecs(.1);
        end
        WaitSecs(.1*subjID);
        
    elseif AUTOMATIC_PROGRESS == 0
        
        %wait for key press
        [~, keyCode]= KbPressWait([]); %startSecs+3);
        keyCode = find(keyCode, 1);
        while keyCode ~= key_block_start(end)
            WaitSecs(.005);
            [~, keyCode]= KbPressWait(); %startSecs+3);
            keyCode = find(keyCode, 1);
        end
        
    end
    
elseif ~isempty(iBlock)     
    
    if AUTOMATIC_PROGRESS == 1
        
        while numel(dir([temp_folder '/block_' num2str(iBlock) '.txt'])) < 1 %numel(dir([temp_folder '/block_' num2str(iBlock) '_*.txt'])) < numSUBs
            WaitSecs(.1);
        end
        
    elseif AUTOMATIC_PROGRESS == 0
        
        % START BLOCK: Press special key to START BLOCK % "gnirob"
        RestrictKeysForKbCheck([key_block_start(iBlock)]);
        [~, keyCode]= KbPressWait(); %startSecs+3);
        keyCode = find(keyCode, 1);
        while keyCode ~= key_block_start(iBlock)
            WaitSecs(.005);
            [~, keyCode]= KbPressWait(); %startSecs+    3);
            keyCode = find(keyCode, 1);
        end
        
        
    else
        fprintf("ERROR! VARIABLE AUTOMATIC_PROGRESS NOT FOUND!");
    end
end

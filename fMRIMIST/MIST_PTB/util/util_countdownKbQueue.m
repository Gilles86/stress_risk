
function [trigger_onsets] = util_countdownKbQueue(MRI,length,screenwindow,trigger)

%==========================================================================
% draw count down (count fixed number = beh, or TRs = MRI)
% isabella.wagner@univie.ac.at
%==========================================================================

trigger_onsets = 0;

if MRI == false
    
    minus = 0;
    
    for i = 1:length
        
        DrawFormattedText(screenwindow, num2str(length - minus), 'center', 'center');
        Screen('Flip',screenwindow);
        
        WaitSecs(1);
        
        minus = minus + 1;
        
    end
    
else
    
    % from Annabel:
    % adapted by: Peter Vavra + Annabel LV
    % version: 2017/07/04
    
    nEvents = 0;
    
    % ----------------------------------------
    % count triggers until 6 volumes scanned
    % ----------------------------------------
    
    KbQueueCreate(deviceIndex);
    KbQueueStart(deviceIndex);
    while nEvents < length
        
        [ pressed, firstPress]=KbQueueCheck(deviceIndex);
        timeSecs = firstPress(find(firstPress)); %#ok<FNDSB>
        %
        %
        %         WaitSecs(0.001);
        if pressed
            if firstPress(trigger)
                
                nEvents = nEvents + 1;
                timeSecs = firstPress(find(firstPress)); %#ok<FNDSB>
                
                trigger_onsets(nEvents,1) = timeSecs;
                
                % draw countdown
                
                DrawFormattedText(screenwindow, num2str(length - nEvents), 'center', 'center');
                Screen('Flip',screenwindow);
                
                %clear response from buffer
                %
                %             keyCode(1,trigger) = 0;
                %
                %             while KbCheck; end
                
                % log status to console
                
                fprintf('trigger nr: %i  -- timestamp: %f\n', nEvents, trigger_onsets(nEvents,1));
            end
        end
        
    end
    KbQueueRelease(deviceIndex);
end



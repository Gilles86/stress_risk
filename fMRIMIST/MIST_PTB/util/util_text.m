function util_text(screenWindow,TextFont,TextSize,TextColor,TextStyle) 

%==========================================================================
% parm = struct with settings
% TextFont = 'Arial'
% TextSize = 26
% TextColor = [255, 255, 255] for white
% TextStyle = 0=normal,1=bold,2=italic,4=underline,8=outline,32=condense,64=extend

% set text style for PTB
% isabella.wagner@univie.ac.at
%==========================================================================

Screen('TextFont',screenWindow, TextFont);
Screen('TextSize',screenWindow, TextSize);
Screen('TextStyle', screenWindow, TextStyle);
Screen('TextColor', screenWindow, TextColor);
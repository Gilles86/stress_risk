
function util_draw_waitmri(screenwindow)

%==========================================================================
%
% util_draw_waitmri(screenwindow)
%
% screenwindow = screen window index
%
% 'Warten auf Scanner ...'
% isabella.wagner@univie.ac.at
%
%==========================================================================

DrawFormattedText(screenwindow, 'Waiting for the Scanner ...', 'center', 'center');

Screen('Flip', screenwindow);
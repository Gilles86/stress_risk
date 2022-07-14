
function util_fixpoint(screenw,background,color,pos)

%==========================================================================
% draw fixation point
% isabella.wagner@univie.ac.at
%==========================================================================

Screen('FillRect', screenw, background);

Screen('FillOval', screenw, color, pos);


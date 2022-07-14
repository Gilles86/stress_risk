function drawText(window, text, color, size, box)

if nargin < 5
    box = [];
end

Screen('TextSize', window, size);
DrawFormattedText(window, text, 'center', 'center', color, [], [], [], [], [], box);

end

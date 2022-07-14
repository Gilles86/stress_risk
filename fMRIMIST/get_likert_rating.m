function final_opt = get_likert_rating(w, wx, hx, data, q_for_show)
%%

nScaleColumns = 7; % Likert Scale
fontsizes  = data.PTB.fontsizes;

% keys
KbName('UnifyKeyNames');
escapeKey = KbName('tab');
% key to confirm choice???
key_space = KbName('3#');
% what are the right and left keys???
possible_keys = ['2@';'4$'];%['1!'; '2@' ;'3#' ;'4$' ;'5%';'6^'];
for ii = 1:length(possible_keys)
    key(ii) = KbName(possible_keys(ii,:));
end
RestrictKeysForKbCheck([escapeKey, key(1:length(possible_keys)) ,key_space ]);
ListenChar(-1);

colors     = data.PTB.colors;
backcolor  = colors.backcolor;
owncolor   = colors.owncolor;
textcolor  = colors.textcolor;
othercolor = colors.othercolor;

Screen('TextSize', w, fontsizes.text);
Screen(w, 'FillRect', colors.backcolor);

scale_position = - floor(hx * .1); % Move vertically
%text_position = (hx * .1); % Below the Scale

%
% Scale Parameters
hori_bar_mat = 0 * ones([floor(hx*(.1/10)) floor(wx*(1/2))]);
hori_bar_texture = Screen('MakeTexture', w, hori_bar_mat);
hori_bar_size = size(hori_bar_mat);
vert_bar_mat = 0 * ones([floor(hx*(.25/10)) floor(wx*(1/300))]);
vert_bar_texture = Screen('MakeTexture', w, vert_bar_mat);
vert_bar_size = size(vert_bar_mat);

cp = [floor(wx*.5) floor(hx*.5)]; %Center point
hori_bar_pos = [floor(cp(1) - .5*hori_bar_size(2)),...
    floor(cp(2) - .5*hori_bar_size(1)) - scale_position,...
    floor(cp(1) + .5*hori_bar_size(2)),...
    floor(cp(2) + .5*hori_bar_size(1)) - scale_position];

%wait for key press
keyCode=-99;

Screen('DrawTexture', w, hori_bar_texture,...
    [0 0 hori_bar_size(2) hori_bar_size(1)], hori_bar_pos);
% Vert bars draw

xRange = linspace(hori_bar_pos(1),hori_bar_pos(3),nScaleColumns);

for xPos = xRange
    vert_bar_pos = [ xPos - vert_bar_size(2),...
        mean([hori_bar_pos(2) hori_bar_pos(4)]) - (.5*vert_bar_size(1)),...
        xPos + vert_bar_size(2),...
        mean([hori_bar_pos(2) hori_bar_pos(4)]) + (.5*vert_bar_size(1)),...
        ];
    Screen('DrawTexture', w, vert_bar_texture,...
        [0 0 vert_bar_size(2) vert_bar_size(1)], vert_bar_pos);
end

yPos =  .5 * (vert_bar_pos(2)+vert_bar_pos(4)) - .08*hx ;
DrawFormattedText(w,q_for_show,'center',hx/3,textcolor);

%create numbers
i = 1;
for xPos = xRange
    DrawFormattedText(w,num2str(i),xPos-wx*.006,hx*0.7,textcolor);
    i = i + 1;
end

DrawFormattedText(w,' Strongly \nDisagree',xRange(1)-xRange(2)*.35,  .5 * (vert_bar_pos(2)+vert_bar_pos(4)) ,textcolor);
DrawFormattedText(w,'Strongly \n  Agree',xRange(nScaleColumns)+xRange(1)*.1,  .5 * (vert_bar_pos(2)+vert_bar_pos(4)) ,textcolor);

DrawFormattedText(w,'Please rate the statement by pressing left or right!','center',hx*.85,textcolor);
curr_opt = 4;

head   = [ xRange(curr_opt) , yPos ]; % coordinates of head
width  = 25;           % width of arrow head
points = [ head-[width/1.5,0]         % left corner
    head+[width/1.5,0]         % right corner
    head+[0,width] ];      % vertex
Screen('FillPoly', w, owncolor, points);

Screen(w,'Flip');


WaitSecs(.3)
while keyCode ~= key_space | keyCode==-99

    Screen('DrawTexture', w, hori_bar_texture,...
        [0 0 hori_bar_size(2) hori_bar_size(1)], hori_bar_pos);
    % Vert bars draw

    xRange = linspace(hori_bar_pos(1),hori_bar_pos(3),nScaleColumns);

    for xPos = xRange
        vert_bar_pos = [ xPos - vert_bar_size(2),...
            mean([hori_bar_pos(2) hori_bar_pos(4)]) - (.5*vert_bar_size(1)),...
            xPos + vert_bar_size(2),...
            mean([hori_bar_pos(2) hori_bar_pos(4)]) + (.5*vert_bar_size(1)),...
            ];
        Screen('DrawTexture', w, vert_bar_texture,...
            [0 0 vert_bar_size(2) vert_bar_size(1)], vert_bar_pos);
    end

    yPos =  .5 * (vert_bar_pos(2)+vert_bar_pos(4)) - .08*hx ;

    %create numbers
    i = 1;
    for xPos = xRange
        DrawFormattedText(w,num2str(i),xPos-wx*.006,hx*0.7,textcolor);
        i = i + 1;
    end

    WaitSecs(.005);
    [~, keyCode]= KbPressWait(-1); %startSecs+3);
    keyCode = find(keyCode, 1);

    switch keyCode
        case (key(1)) % right key move
            curr_opt = circshift([1:nScaleColumns],-curr_opt+1-1);
            curr_opt = curr_opt(1);
        case (key(2)) % left key move
            curr_opt = circshift([1:nScaleColumns],-curr_opt+1+1);
            curr_opt = curr_opt(1);
        case escapeKey
            sca;
            return;
        case key_space
            WaitSecs(.5)
            if exist('curr_opt','var')
                curr_opt;
            else
            end
        case -99
            keyCode = -99;

    end

    if  ~isempty(curr_opt)
        head   = [ xRange(curr_opt) , yPos ]; % coordinates of head
        width  = 25;           % width of arrow head
        points = [ head-[width/1.5,0]         % left corner
            head+[width/1.5,0]         % right corner
            head+[0,width] ];      % vertex
        Screen('FillPoly', w, owncolor, points);

        DrawFormattedText(w,'Press the "down key" to confirm your decision!','center',hx*.85,textcolor);
    else
        DrawFormattedText(w,'Please rate the statement by pressing left or right!','center',hx*.85,textcolor);

    end

    DrawFormattedText(w,q_for_show,'center',hx/3,textcolor);

    DrawFormattedText(w,' Strongly \nDisagree',xRange(1)-xRange(2)*.35,  .5 * (vert_bar_pos(2)+vert_bar_pos(4)) ,textcolor);
    DrawFormattedText(w,'Strongly \n  Agree',xRange(nScaleColumns)+xRange(1)*.1,  .5 * (vert_bar_pos(2)+vert_bar_pos(4)) ,textcolor);


    Screen(w,'Flip');

end

final_opt = curr_opt;


end


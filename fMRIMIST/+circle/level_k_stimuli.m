function level_k_stimuli(data,w,wx,hx,choice_string_own,choice_string_other,stateTrial)
%
% draw CHASE game circle and, depending on trial-state, choices and/or feedback
%

arrow_type = 2; % 1 for old ("greater-than"), 2 for new (arrow)

%% extract variables
trial = numel(choice_string_own);

strat_space = data.nActions;
fontsizes   = data.PTB.fontsizes;
flip_circle = data.flip_circle;
pay_matrix_A = data.pi_A;
pay_matrix_B = data.pi_B;

colors     = data.PTB.colors;
backcolor  = colors.backcolor;
owncolor   = colors.owncolor;
textcolor  = colors.textcolor; 
othercolor = colors.othercolor;

Screen('TextSize', w, fontsizes.payoffs*0.9);
Screen(w, 'FillRect', colors.backcolor);

%% circle and choice options
% settings
xCenter = wx/2;
yCenter = hx/2;             % hx/3
radius       = round(hx/4.5); % hx/6
radiusOption = round(hx/20);  % hx/25

textOffset = -0; % 0 for ETH lab

angleOffset = -pi/2-pi/strat_space; % +pi/2

% calculate positions
angles = (2*pi*[strat_space:-1:1])./strat_space;
xPos   = round(radius * cos(angles+angleOffset) + xCenter);
yPos   = round(radius * -sin(angles+angleOffset) + yCenter); 

% arrows
switch arrow_type
    case 1
        arrowOffset = 0.96; % 0.91?
        rectSize    = [220 140]*0.45;
        arrowRGB = repmat(colors.backcolor,[220,140,3]);
        arrowTexture = Screen('MakeTexture',w,arrowRGB);
        Screen('TextSize',arrowTexture,200);
        DrawFormattedText(arrowTexture, '<','center','center',textcolor);
    case 2
        arrowOffset = 0.975;
        rectSize    = [100 100];
        arrowRGB = repmat(colors.backcolor(1),[100,100,3]);
        arrowTexture = Screen('MakeTexture',w,arrowRGB);
        arrow_radius  = 18;
        tail_angle = 60; % 0-90
        radians    = tail_angle*pi/180;
        points = [50 50] + ...
                 [ [-arrow_radius 0] % tip
                   [cos(radians) sin(radians)]*arrow_radius
                   [0 0]
                   [cos(radians) -sin(radians)]*arrow_radius ];
        Screen('FillPoly', arrowTexture, textcolor, points);
end    
xPosArrow = round(radius*arrowOffset*cos(angles+pi/2-pi/strat_space) + xCenter); % + pi/strat_space for half-step shift (0.91/0.96)
yPosArrow = round(radius*arrowOffset*-sin(angles+pi/2-pi/strat_space) + yCenter); 
for iOption = 1:strat_space
    %DrawFormattedText2('<size=50> >','win',w,'sx',xPosArrow(iOption),'sy',yPosArrow(iOption),'xalign', 'center','yalign','center', 'transform' ,{'rotate',225}, 'baseColor', textcolor );
    arrowRect = CenterRectOnPoint([0 0 rectSize],xPosArrow(iOption),yPosArrow(iOption)); %ETH lab .. , otherwise 2*1
    rotation = round(rem(360/strat_space*iOption - 360/strat_space/2 + 180,360));
    Screen('DrawTexture', w, arrowTexture, [], arrowRect, rotation, [], 0);
end
    
% main circle
draw_circle(w,textcolor,xCenter,yCenter,radius,0,textcolor,5);

% options
positions = circshift(1:strat_space,flip_circle);

for iOption = 1:strat_space
    x = xPos(iOption);
    y = yPos(iOption);
    
    if iOption == data.game.focal_own
        penWidth = 8;
    else
        penWidth = 4;
    end
        
    % circles
    draw_circle(w,backcolor,x,y,radiusOption,0);
    draw_circle(w,backcolor,x,y,radiusOption,0,textcolor,penWidth);
    
    % text
    textRect = CenterRectOnPoint([0 0 100 100],x,y+textOffset);
    DrawFormattedText(w,num2str(positions(iOption)), 'center', 'center', textcolor, [],[],[],[],[],textRect);
end
    
% Screen('Flip', w);
% WaitSecs(0.5);
% KbWait();
    
% % %     %draw arrows
% % %     DrawFormattedText2('<size=50> >','win',w,'sx',wx/2+sin(pi/4)*hx/4.55 ,'sy',hx/2-cos(pi/4)*hx/4.55,'xalign', 'center','yalign','center', 'transform' ,{'rotate',225}, 'baseColor', textcolor );
% % %     DrawFormattedText2('<size=50> >','win',w,'sx',wx/2+sin(3*pi/4)*hx/4.55 ,'sy',hx/2-cos(3*pi/4)*hx/4.55,'xalign', 'center','yalign','center', 'transform' ,{'rotate',315} ,'baseColor', textcolor);
% % %     DrawFormattedText2('<size=50> >','win',w,'sx',wx/2+sin(5*pi/4)*hx/4.55 ,'sy',hx/2-cos(5*pi/4)*hx/4.55,'xalign', 'center','yalign','center','transform' ,{'rotate',45} ,'baseColor', textcolor);
% % %     DrawFormattedText2('<size=50> >','win',w,'sx',wx/2+sin(7*pi/4)*hx/4.55 ,'sy',hx/2-cos(7*pi/4)*hx/4.55,'xalign', 'center','yalign','center', 'transform' ,{'rotate',135} ,'baseColor', textcolor); 
      
% if trial > 0 
%     DrawFormattedText(w,strcat('Your score: ', num2str(score_A) , '\nOther''s score: ',num2str(score_B)), 'center', 'center', textcolor, [],[],[],[],[],[wx -hx*4/5 0 hx]);      
% end
    
%% trial-state specific coloring
% depending on trial, draw the corresponding state
if stateTrial==1

    drawFixationCross(w,fontsizes,textcolor,wx,hx);
    %DrawFormattedText2('+','win',w,'sx',wx/2 ,'sy',hx/2,'xalign', 'center','yalign','center','textColor',[0 255 0] , 'resetStyle', 1 ); 
    %DrawFormattedText(w,'Press now', 'center', 'center', col{1}, [],[],[],[],[],[wx -mac*fontsizes.cross/2 0 hx]);
    
elseif stateTrial==2
    
    drawFixationCross(w,fontsizes,owncolor,wx,hx);
    %DrawFormattedText2('<size=60>+','win',w,'sx',wx/2 ,'sy',hx/2,'xalign', 'center','yalign','center','baseColor',textcolor ); 
    
elseif stateTrial==3
    
    drawFixationCross(w,fontsizes,owncolor,wx,hx);
    %DrawFormattedText2('<size=60>+','win',w,'sx',wx/2 ,'sy',hx/2,'xalign', 'center','yalign','center','baseColor',owncolor ); 

    %recode choice to up/right/down/left
    mapped_choice_own2 = rem(choice_string_own(end) + flip_circle - 1, strat_space) + 1;
    if flip_circle>0
        mapped_choice_own = choice_string_own(end) + flip_circle;
        mapped_choice_own(mapped_choice_own>strat_space)=mapped_choice_own-strat_space;           
    else
        mapped_choice_own=choice_string_own(end);  
    end
    assert(mapped_choice_own == mapped_choice_own2);
    
    % colored circle
    draw_circle(w,owncolor,xPos(mapped_choice_own),yPos(mapped_choice_own),radiusOption,0);
    
    % draw text again
    textRect = CenterRectOnPoint([0 0 100 100],xPos(mapped_choice_own),yPos(mapped_choice_own) + textOffset);
    DrawFormattedText(w,num2str(positions(mapped_choice_own)), 'center', 'center', textcolor, [],[],[],[],[],textRect);
    
    % Tell to wait for the opponent
    %DrawFormattedText(w,'Waiting for opponent...', 'center', 'center', col{1}, [],[],[],[],[],[wx -mac*fontsizes.cross/2 0 hx]);   
    
elseif stateTrial == 4
    
    drawFixationCross(w,fontsizes,owncolor,wx,hx);
    %DrawFormattedText2('<size=60>+','win',w,'sx',wx/2 ,'sy',hx/2,'xalign', 'center','yalign','center','baseColor', [200 0 0] );
   
    % get payoffs
    if choice_string_own(end)==-99
        pay_own=-99;
    else
        pay_own = pay_matrix_A(choice_string_own(end),choice_string_other(end));
        pay_other = pay_matrix_B(choice_string_other(end),choice_string_own(end));
    end  
    feedback1=strcat([ num2str(pay_own)]);
    feedback2=strcat([ num2str(pay_other)]);
    
    if strcmp(feedback1,'1')
        feedback1 = '+1';
    end
    if strcmp(feedback2,'1')
        feedback2 = '+1';
    end
    
    %DrawFormattedText(w,feedback1, 'center', 'center', owncolor, [],[],[],[],[],[wx -hx*4/5 0 hx]);
    %DrawFormattedText(w,feedback2, 'center', 'center', othercolor, [],[],[],[],[],[wx +hx*4/5 0 hx]);
        
    %text_round= cell(2*trial,1);
    %text_round(1:2*trial,1) ={' '};
    %text_round(2*trial-1,1)= {'LastChoice'};
   
    %recode choice to up/right/down/left
    mapped_choice_own   = rem(choice_string_own(end) + flip_circle - 1, strat_space) + 1;
    mapped_choice_other = rem(choice_string_other(end) + flip_circle - 1, strat_space) + 1;
       
    % ~~~~~~~~~~ OWN ~~~~~~~~~~ %
    choice = mapped_choice_own(end);
    color  = owncolor;
    feedback = feedback1;
    
    % colored circle
    draw_circle(w,color,xPos(choice),yPos(choice),radiusOption,0);
    
    % draw text again
    textRect = CenterRectOnPoint([0 0 100 100],xPos(choice),yPos(choice) + textOffset);
    DrawFormattedText(w,num2str(positions(choice)), 'center', 'center', textcolor, [],[],[],[],[],textRect);
    
    % colored feedback
    xPosFb   = round(radius * 0.5 * cos(angles(choice)+angleOffset) + xCenter);
    yPosFb   = round(radius * 0.5 * -sin(angles(choice)+angleOffset) + yCenter); 
    textRectFb = CenterRectOnPoint([0 0 100 100],xPosFb,yPosFb + textOffset);
    DrawFormattedText(w,feedback, 'center', 'center', color, [],[],[],[],[],textRectFb);
    
    if mapped_choice_own(end)==mapped_choice_other(end)
        full_circ=1;
    else
        full_circ=0;
    end
    
    % ~~~~~~~~~~ OTHER ~~~~~~~~~~ %
    choice = mapped_choice_other(end);
    color  = othercolor;
    feedback = feedback2;
    
    % colored circle
    draw_circle(w,color,xPos(choice),yPos(choice),radiusOption,full_circ);
    
    % draw text again
    textRect = CenterRectOnPoint([0 0 100 100],xPos(choice),yPos(choice) + textOffset);
    DrawFormattedText(w,num2str(positions(choice)), 'center', 'center', textcolor, [],[],[],[],[],textRect);
    
    % colored feedback
    xPosFb   = round(radius * 0.5 * cos(angles(choice)+angleOffset) + xCenter);
    yPosFb   = round(radius * 0.5 * -sin(angles(choice)+angleOffset) + yCenter); 
    textRectFb = CenterRectOnPoint([0 0 100 100],xPosFb,yPosFb + textOffset);
    DrawFormattedText(w,feedback, 'center', 'center', color, [],[],[],[],[],textRectFb);
    
	elseif stateTrial==99
       
        drawFixationCross(w,fontsizes,[255 0 0],wx,hx);
% %         DrawFormattedText(w,'X', 'center', 'center', [255 0 0], [],[],[],[],[],[wx 0 0 hx]);
        
end

end

% ============================================================================ %

function drawFixationCross(w,fontsizes,color,wx,hx)

oldTextSize=Screen('TextSize', w, fontsizes.cross); % *1.2
rect = [wx -hx/40 0 hx]; % [wx -hx/403*2 0 hx/3*2]
DrawFormattedText(w,'+', 'center', 'center', color, [],[],[],[],[],rect);
Screen('TextSize', w, oldTextSize);

end
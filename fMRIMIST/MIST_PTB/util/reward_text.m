function text = reward_text(what)

%==========================================================================
% text settings for reward paradigm
% isabella.wagner@univie.ac.at
%==========================================================================

% 1. some textparts
%--------------------------------------------------------------------------

buttonStart = 'STARTE den Durchgang mit einer beliebigen Taste...';

buttonContinue = 'WEITER mit beliebiger Taste...';

% 2. put screen text together
%--------------------------------------------------------------------------

switch what
    
    case 'slide1'
        
        intro = [...
            'Im Folgenden wirst Du stets zwei Symbole sehen.\n\n',...
            'Wähle immer eines der Beiden aus.\n\n\n\n',...
             ];
        
        text = [intro,buttonContinue];
    case 'slide2'
        
        intro = [...
           
            'Für jede Auswahl, kann man PUNKTE bekommen oder verlieren;\n\n',...
            'wobei man meistens für eines der Symbole häufiger Punkte \n\n',...
            'bekommen kann, als für das Andere.\n\n \n\n',...
             ];
        
        text = [intro,buttonContinue];
    case 'slide3'
        
        intro = [...
            'Allerdings ändert sich während des Spieles welches Symbol \n\n',...
            'häufiger Punkte bekommt.\n\n',...
            'DEINE AUFGABE ist es, herauszufinden, bei welchem Symbol \n\n',...
            'Du mehr Punkte gewinnen kannst.\n\n\n\n',...
            ];
        
        text = [intro,buttonContinue];
        
    case 'slide4'
        
           
        intro = [...
            'Welches Symbol einem Punkte gibt, ist unabhängig von der \n\nPosition am Bildschirm,',...
            'oder davon, wann es Dir gezeigt wird.\n\n\n\n',...
            'Verwende für Deine Auswahl den LINKEN und RECHTEN Knopf,\n\n',...
            'mit dem ZEIGE- und MITTELFINGER deiner rechten Hand.\n\n\n\n',...
            ];
        
        text = [intro,buttonContinue];
    case 'slide5'
        
           
        intro = [...
            'Für jede Auswahl hast du 2 Sekunden Zeit. \n\nDanach wird die aktuelle Auswahl grün angezeigt.\n\n\n\n',...
            'Versuche stets so SCHNELL, aber auch so RICHTIG \n\nwie möglich zu antworten.\n\n',...
            'Wenn Du keine Auswahl triffst, \n\nwird DIR ein Punkt abgezogen!\n\n\n\n',...
            ];
        
        text = [intro,buttonContinue];
        
    case 'slide6'
        
        intro = [...
            'Insgesamt wird das Spiel 200 Runden dauern. \n\n',...
            'Umgerechnet bekommst du für jeden Punkt vier Cent.  \n\n\n\n',...
            ];
        
        text = [intro,buttonContinue];
        
    case 'slide7'
        
        intro = [...
            'Bitte vergiss nicht, deinen Kopf stets SO STILL WIE MÖGLICH zu halten!\n\n\n\n',...
            'Hast du noch Fragen?\n\n',...
            'Dann stelle diese bitte JETZT.\n\n\n\n',...
            'Ansonsten,\n\n',...
            ];
        
        text = [intro,buttonStart];
        
    case 'targetYou'
        
        text = 'Mach dich bereit!';
        
        %     case 'targetOther'
        %
        %         text = ['Du spielst f?r ',upper(char(subj2))];
        
        %     case 'you'
        %
        %         text = 'DU';
        %
        %     case 'other'
        %
        %         text = upper(char(subj2));
        %
    case 'win'
        
        text = '+ 1 Punkt';
        
    case 'lose'
        
        text = '- 1 Punkt';
        
    case 'miss'
        
        text = 'zu langsam!';
        
    case 'ende'
        
        text = 'Ende des Durchgangs.';
        
end
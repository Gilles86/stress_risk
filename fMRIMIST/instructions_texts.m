function text = get_instructions(exp_language)

switch exp_language
    case 'EN'
        
        text.focal_own =         'Your special number is: ';
        text.focal_other =       '\n\nYour opponent''s special number is: ';
        text.focal_same  =       '\n\nThe special number is: ';
        text.focal_none  =       '\n\n(No special number)';
        
        text.start_block =      ['Please wait! \n\n',...
                                 'We will proceed as soon as everyone is ready.'];
        
        text.practice_title =    'Practice Session';
        text.practice_info  =   ['To familiarize yourself with the task and the response buttons,\n',...
                                 'you will play a few practice rounds against a random opponent. \n',...
                                 'Please note: you will not be re-matched with this opponent during the real experiment.\n\n ',...
                                 'These practice rounds will not count toward your final payoff.'];
        text.practice_getready = 'Press the SPACE BAR to start';
        text.practice_end =     ['End of practice session!\n\n',...
                                 'Shortly, the actual experiment will start.\n',...
                                 'Remember, within a block (= for 30 rounds), you will always play against the same opponent.\nBut you will be re-matched\nagainst a different opponent at the beginning of a new block.\n\n',...
                                 'Note that all rounds now count toward your final payoff.\n'];

        text.block_indication =  'Match # ';
        text.wait_for_scanner =  'Please wait for the scanner...';
        text.wait_for_opp1 =     'Matching with first opponent...';
        text.wait_for_opp =      'Matching with new opponent...';
        text.get_ready =         'GET READY';
        text.go =                'START';
        text.block_end =        ['Block completed.\n\n',...
                                 'Feel free to take a quick break.']; 

        text.exp_end =          ['You completed the experiment!'];
        
        text.t1_scan =          ['We are done with the main part of the experiment!'];
                             
    case 'DE'
        
        text.focal_own =         'Ihre Bonuszahl ist: ';
        text.focal_other =       '\n\nDie Bonuszahl von Ihrem Mitspieler ist: ';
        text.focal_same  =       'Die Bonuszahl in dieser Runde ist: ';
        text.focal_none  =       '(Keine Bonuszahl)';
        
        text.practice_title =    'Proberunden';
        text.practice_info =    ['Damit Sie sich mit dem Spiel vertraut machen können, folgen nun einige Proberunden.\n',...
                                 'Während den Proberunden wählt ein Computer zufällig eine Entscheidung aus.\n\n ',...
                                 'Die Punkte während diesen Runden werden nicht gezählt.'];
        text.practice_getready = 'Gleicht geht''s los...';
        text.practice_end =     ['Ende der Proberunden\n\n\n',...
                                 'In Kürze wird das richtige Experiment beginnen.\n\n',...
                                 'Denken Sie daran: Ab jetzt werden Ihre Punkte aus jeder Runde\n',...
                                 'für die Bezahlung am Ende des Experimentes zusammengezählt.'];

        text.block_indication =  'Block # ';
        text.wait_for_scanner =  'Warten auf den MRT-Scanner...';
        text.wait_for_opp =      'Bitte machen Sie sich bereit...';
        text.go =                'START';
        text.block_end =        ['Block beendet\n\n',...
                                 'Sie können eine kurze Verschnaufpause machen.\n',...
                                 'Wir werden in Kürze mit Ihnen sprechen.']; 

        text.exp_end =          ['Das war''s - Sie haben''s geschafft!\n\n',...
                                 'Wir werden uns in Kürze bei Ihnen melden.'];
                             
end

end
        
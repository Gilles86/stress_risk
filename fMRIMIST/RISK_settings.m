function [data,settings] = RISK_settings(data)
%
% settings for Risk task

%% experiment

% what to run
F.MAC          = 0; %when running on mac
F.TESTING      = 0; % smaller screen
F.MIST         = 1; % 0 for skiping the MIST task, for testing
F.RISK_TASK    = 1; % 0 for skiping the RISK task, for testing

F.MRISCREEN    = 1;

F.MRISCANNING  = 1;
F.EYETRACKING  = 1; 

data.speedup_factor = 1; % 1 = regular timing as in scanner, higher = faster
%%

data.config.exp_language    = 'EN'; % 'EN', 'DE'     

% payoffs
ShowUp       = 0;
ExchangeRate = 1;

%%

settings.game.show_up       = ShowUp;
settings.game.exchange_rate = ExchangeRate;

data.game = settings.game;

%% PTB

data.PTB.skipsynctest = 1;
data.PTB.mac = 1;

data.PTB.colors.backcolor  = [178.5 178.5 178.5];
data.PTB.colors.owncolor   = [53 77 229];
data.PTB.colors.othercolor = [50 100 10];
data.PTB.colors.textcolor  = [0 0 0]; %[118 60 206];

data.PTB.font = 'Helvetica';
data.PTB.fontsizes.text    = 30;
data.PTB.fontsizes.choices = 50;
data.PTB.fontsizes.payoffs = 40;
data.PTB.fontsizes.cross   = 60;

%% renaming

data.flags = F;

end

function [beta,noisy_trial,success,tie_breaker,rep_bounds] = get_noise_level(iTrial,data,player)

level_k     = data.(player).params(1);
skeweness   = 1;
rep_bounds  = NaN; % circuit breaker
success_criterion = 0.5;
time_horizon      = 5;

% +++++++++++++++++++++++++++++ FINAL LEVELS +++++++++++++++++++++++++++++++++ %
%noise_level = 'noCircuit_sess5_same'; % << DEFAULT for first session
noise_level = 'noCircuit_sess5_less'; % << LESS noise (if suspicion in human-human data same)
% noise_level = 'withCircuit';          % << MORE noise (if no suspcicion in human-human data)
% ++++++++++++++++++++++++++++ /FINAL LEVELS +++++++++++++++++++++++++++++++++ %

switch level_k
    
    % level-0
    case 0
        
        switch noise_level
                
% %             case 3 % high noise   <<< this _might've_ been too low
% %                 streak_bounds     = [0,2];
% %                 skeweness         = 1.5;
                
            case 'withCircuit'
                streak_bounds     = [1,2];
                skeweness         = 1.3;
                rep_bounds        = [4,5]; % for circuit breaker
            
            case 'noCircuit_sess5_same'
                streak_bounds     = [0,2];
                skeweness         = 1.5;
            
            case 'noCircuit_sess5_less'
                streak_bounds     = [1,2];
                skeweness         = 1.3;
                
% %             case 4 % maximum noise  <<< this was too high
% %                 streak_bounds     = [0,2];
% %                 time_horizon      = 4;
% %                 skeweness         = 0.8;
                
        end
        
    % levels 1
    case 1
        
        switch noise_level
                
%             case 3 % high noise
%                 streak_bounds     = [1,3];
%                 skeweness         = 1.1;
                
            case 'withCircuit' % i.e. only more noise here
                streak_bounds     = [1,2];
                skeweness         = 1;
            
            case 'noCircuit_sess5_same'
                streak_bounds     = [1,3];
                skeweness         = 0.8;
            
            case 'noCircuit_sess5_less'
                streak_bounds     = [1,3];
                skeweness         = 1.3;
                
% %             case 4 % maximum noise  <<< maybe (?) too high
% %                 streak_bounds     = [0,2];
% %                 time_horizon      = 4; % i.e. need 2/4
% %                 skeweness         = 1.4;

        end
        
    % levels 2
    case 2
        
        switch noise_level
                
%             case 3 % high noise
%                 streak_bounds     = [1,3];
%                 skeweness         = 1.1;
                
            case 'withCircuit' % i.e. only more noise here
                streak_bounds     = [1,3];
                skeweness         = 1.4;
                rep_bounds        = [4,5]; % for circuit breaker
            
            case 'noCircuit_sess5_same'
                streak_bounds     = [1,3];
                skeweness         = 1.1;
            
            case 'noCircuit_sess5_less'
                streak_bounds     = [1,3];
                skeweness         = 1.3;
                
% %             case 4 % maximum noise  <<< maybe (?) too high
% %                 streak_bounds     = [0,2];
% %                 time_horizon      = 4; % i.e. need 2/4
% %                 skeweness         = 1.4;
                
        end        
end

streak_max = randi([3 4]); % for loose/tie

types = {'wins','ties','losses'};
for i_type = 1:3
    type = types{i_type};
    switch type
        case 'wins',   recent.(type) = (data.score_A(max(1,iTrial-time_horizon):end) > 0); n_trials_back = streak_bounds(2);
        case 'ties',   recent.(type) = (data.score_A(max(1,iTrial-streak_max):end) == 0);  n_trials_back = streak_max;
        case 'losses', recent.(type) = (data.score_A(max(1,iTrial-streak_max):end) < 0);   n_trials_back = streak_max;
    end
    for n_trials = 1:n_trials_back%streak_bounds(2)
        if sum(recent.(type)(max(1,end-n_trials+1):end)) < n_trials
            streak.(type) = n_trials-1;
            break
        else
            streak.(type) = n_trials;
        end
    end
end

success = sum(recent.wins)/numel(recent.wins);

beta = 10;
noisy_trial = 0;
tie_breaker = 0;
if streak.losses >= streak_max || streak.ties >= streak_max
    beta = 1e-3;
    [noisy_trial,tie_breaker] = deal(1);
elseif success >= success_criterion && streak.wins >= streak_bounds(1)
    chance_level = (1/(streak_bounds(2) + 1 - streak.wins))^skeweness;
    if rand < chance_level || streak.wins >= streak_bounds(2)
    	beta = 1e-3;
        noisy_trial = 1;
    end
end

end
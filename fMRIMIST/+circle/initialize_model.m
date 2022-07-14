function data = initialize_model(data,settings,player)

data.(player).model = settings.(player).model;
        
switch settings.(player).model
    
    case 'bot'
        
        % parameters
        data.(player).level_k = settings.(player).params(1);
        data.(player).memory  = settings.(player).params(2);
        data.(player).beta    = settings.(player).params(3);
        
        % variables
%         data.(player).level0_bias    = data.(['focal_' player]);
        data.(player).level0_bias    = data.game.(['bonus_' player]);
        data.(player).tlength        = 3;
        data.(player).maxtlength     = 10;
        
        % model function
        data.(player).simulate_trial_func = @simulate_trial__Bot;
        
    case 'LKbot'
        
        % parameters
        data.(player).params = settings.(player).params;
        data.(player).blf    = settings.(player).blf;
        
        % variables (only these, as no beliefs)
        [data.(player).f_mat_self,data.(player).f_mat_opp] = deal(NaN(data.nTrials,data.nActions));
        [data.(player).f_mat_self(1:data.nGreedyTrials,:),...
          data.(player).f_mat_opp(1:data.nGreedyTrials,:)] = deal(repmat(1/data.nActions,[data.nGreedyTrials,data.nActions]));
        
        % !! difference to 'LK': success vector to adapt noise !! 
        [data.(player).success,data.(player).curr_beta] = deal(NaN(data.nTrials,1));
        [data.(player).noisy_trial,data.(player).noise_breaker,data.(player).tie_breaker,data.(player).circuit_breaker,] = deal(zeros(1,data.nTrials));
        data.(player).success(2)   = 1/data.nActions;
        data.(player).curr_beta(2) = 4;
        
        % model function
        data.(player).simulate_trial_func = @circle.simulate_trial__LKbot;
        
    case {'LK','LKmix','LKswitch'}
        
        % parameters
        data.(player).params = settings.(player).params;
        data.(player).blf    = settings.(player).blf;
        
        % variables (only these, as no beliefs)
        [data.(player).f_mat_self,data.(player).f_mat_opp] = deal(NaN(data.nTrials,data.nActions));
        [data.(player).f_mat_self(1:data.nGreedyTrials,:),...
          data.(player).f_mat_opp(1:data.nGreedyTrials,:)] = deal(repmat(1/data.nActions,[data.nGreedyTrials,data.nActions]));
        
        % model function
        switch settings.(player).model
            case 'LK', data.(player).simulate_trial_func = @simulate_trial__LK;
            case 'LKmix', data.(player).simulate_trial_func = @simulate_trial__LKmix;
            case 'LKswitch', data.(player).simulate_trial_func = @simulate_trial__LKswitch;
        end
        
    case {'CH','CHbot'}
        
        % parameters
        data.(player).params = settings.(player).params;
        data.(player).blf    = settings.(player).blf;
        
        % variables
        [data.(player).f_mat_self,data.(player).f_mat_opp] = deal(NaN(data.nTrials,data.nActions));
        [data.(player).f_mat_self(1:data.nGreedyTrials,:),...
         data.(player).f_mat_opp(1:data.nGreedyTrials,:)] = deal(repmat(1/data.nActions,[data.nGreedyTrials,data.nActions]));
        
        switch settings.(player).model
            case 'CH',    kMax = data.(player).params(1);
            case 'CHbot', kMax = get_MAX_LEVEL_CHbot+1;
        end
        
        data.(player).subj_L_k.(['k' num2str(kMax)]) = NaN(data.nTrials,kMax);
        data.(player).subj_p_k.(['k' num2str(kMax)]) = NaN(data.nTrials,kMax);
        data.(player).subj_beliefs.(['k' num2str(kMax)]) = ones(1,kMax)/kMax; % priors
        
        % model function
        switch settings.(player).model
            case 'CH', data.(player).simulate_trial_func = @simulate_trial__CH;
            case 'CHbot', data.(player).simulate_trial_func = @simulate_trial__CHbot;
        end
        
    otherwise
        
        error('Cannot initialize (unknown model).');

end

end
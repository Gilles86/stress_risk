function data = simulate_trial__LKbot(iTrial,data,player) 
%
% same as LK, but with adaptive noise based on (subject) success rate target
%

VERBOSE = 0;

% need
blf      = data.(player).blf;
rsp      = 'softmax';

nActions = data.nActions;

nLevels  = data.(player).params(1) + 1;
% % beta_fix = data.(player).params(end);
success_alpha = data.(player).params(end-1);
sensitivity   = data.(player).params(end);

switch player
    case 'A'
        pi_own   = data.pi_A;
        pi_other = data.pi_B;
    case {'B','bot'}
        pi_own   = data.pi_B;
        pi_other = data.pi_A;
end

% initialize
p_a_own = NaN(nLevels,nActions); 
    
% extract relevant trial
f_self = data.(player).f_mat_self(iTrial-1,:)'; % because p(a) is a prediction based the history *up to* the current trial
f_opp  = data.(player).f_mat_opp(iTrial-1,:)';  
   
assert(~any(isnan([f_self;f_opp])),'NaN attractions.');

% === NOISE ADAPTATION === %
[beta,noisy_trial,success,tie_breaker,rep_bounds] = circle.get_noise_level(iTrial,data,player);
data.(player).success(iTrial)     = success;
data.(player).curr_beta(iTrial)   = beta;
data.(player).noisy_trial(iTrial) = noisy_trial;
data.(player).tie_breaker(iTrial) = tie_breaker;
% === /NOISE ADAPTATION === %

% compute strategic response
for level_k = 0:data.(player).params(1)

    % ------------------- (Re-)active strategies ------------------------- %

    if level_k == 0 % subject plays egocentric strategy (<- only strategy neglecting payoff table)
        p_a_own(1,:)      = circle.tomRL_responseFunc(f_self',beta,rsp); 

    elseif level_k == 1 % subject BRs to the other's egocentric strategy
        p_a_belief(1,:)   = circle.tomRL_responseFunc((pi_own*f_opp)',beta,blf); % used for higher levels
        p_a_own(2,:)      = circle.tomRL_responseFunc((pi_own*f_opp)',beta,rsp);

    % ----------------- Influence learner strategies --------------------- %

    elseif level_k == 2 % subject BRs to the other's BR to his own egocentric strategy
        p_a_other         = circle.tomRL_responseFunc((pi_other*f_self)',beta,blf);
        p_a_belief(2,:)   = circle.tomRL_responseFunc((pi_own*p_a_other')',beta,blf); % used for higher levels 
        p_a_own(3,:)      = circle.tomRL_responseFunc((pi_own*p_a_other')',beta,rsp); 

    elseif level_k >= 3 % ...subject adds two steps of reasoning to last estimate of same type (i.e. odd vs even)
        p_a_other             = circle.tomRL_responseFunc((pi_other*p_a_belief(level_k-2,:)')',beta,blf);
        p_a_belief(level_k,:) = circle.tomRL_responseFunc((pi_own*p_a_other')',beta,blf); % used for higher levels 
        p_a_own(level_k+1,:)  = circle.tomRL_responseFunc((pi_own*p_a_other')',beta,rsp); 

    end

end

switch player
    
    case 'A'
        
        % choose action
        data.choice_own(iTrial) = randsample(1:nActions,1,true,p_a_own(end,:));
        data.(player).p_a_own(:,iTrial) = p_a_own(end,:);
        
    case {'B','bot'}
        
        p = p_a_own(end,:);
        
        % exclude model-conform action if noisy trial
        if noisy_trial
            [~,max_idx] = max(p);
            p(max_idx) = 0;
            p = p/sum(p);
            if VERBOSE
                fprintf(2,'\nNOISY TRIAL');
                if tie_breaker
                    fprintf(2,' (tie breaker)\n');
                else
                    fprintf(2,'\n');
                end
            end
        end
        
        % ensure that noisy action isn't repeated too often
        if noisy_trial 
            n_max = randi([1 2]);
            if iTrial > n_max
                prior_noisy_trials = sum(data.(player).curr_beta(max(1,end-n_max+1):end) < 1);
                prior_actions_identical = ~any(diff(data.choice_other(max(1,end-n_max+1):end)));
                if prior_noisy_trials >= n_max && prior_actions_identical
                    p(data.choice_other(end)) = 0;
                    p = p/sum(p);
                    if VERBOSE
                        fprintf(2,'\nNOISE REPETITION BREAKER\n');
                    end
                    data.(player).noise_breaker(iTrial) = 1;
                end     
            end
        end
        
        % 3. criterion: too often the same action was played by human or by bot.
        if ~isnan(rep_bounds)
            max_rep_action = randi(rep_bounds);
            if iTrial >= max_rep_action
                if ~noisy_trial && data.block_level_k(data.iBlock)~=1 && (~any(diff(data.choice_own(max(1,end-max_rep_action+1):end))) || ~any(diff(data.choice_other(max(1,end-max_rep_action+1):end))))
                    [~,max_idx] = max(p);
                    p(max_idx) = 0;
                    p(setdiff(1:nActions,max_idx)) = 1;
                    p = p/sum(p); 
                    if VERBOSE
                        fprintf(2,'\nCIRCUIT BREAKER\n');
                    end
                    data.(player).circuit_breaker(iTrial) = 1;
                end
            end
        end
        
        % choose action
        if VERBOSE
            p
        end
        data.choice_other(iTrial) = randsample(1:nActions,1,true,p);  
        data.(player).p_a_own(:,iTrial) = p;  
           
end

end


function [f_mat_own,f_mat_other] = tomRL_step_level0(type,iTrial,f_mat_own,f_mat_other,choice_own,choice_other,curr_params,varargin)
% 
% update the level-0 attractions, based on a specified learning rule and a given set of parameters
%
% update is based on the actions of the *current trial* and thus gives the attractions that the 
% agent will use on the *next* trial. however, as the update presumably happens during feedback
% of the current trial, this is where the corresponding quantities are stored.
%

nActions = size(f_mat_own,2);

switch type

    case 'RW_freq' % Rescorla-Wagner learning of frequency (parameter determines learning rate)
        
        al = curr_params(1);
% %         assert(0 < al && al < 1,'Learning rate must be in unit interval.');
        
        currTrial = zeros(nActions,1);
        currTrial(choice_own(iTrial)) = 1; %<
        f_mat_own(iTrial,:) = (1-al) * f_mat_own(max(1,iTrial-1),:) + al .* currTrial';

        currTrial = zeros(nActions,1);
        currTrial(choice_other(iTrial)) = 1; %<
        f_mat_other(iTrial,:) = (1-al) * f_mat_other(max(1,iTrial-1),:) + al .* currTrial';

        % add prediction errors
        
    case 'RW_reward' % Rescorla-Wagner learning of reward (parameter determines learning rate)
        
        al = curr_params(1);

        currTrial = zeros(nActions,1);
        currTrial(choice_own(iTrial)) = varargin{1}(iTrial); %< score_own
        f_mat_own(iTrial,:) = (1-al) * f_mat_own(max(1,iTrial-1),:) + al .* currTrial';

        currTrial = zeros(nActions,1);
        currTrial(choice_other(iTrial)) = varargin{2}(iTrial); %< score_other
        f_mat_other(iTrial,:) = (1-al) * f_mat_other(max(1,iTrial-1),:) + al .* currTrial';

    case 'EWA_like' % EWA-style extension of RW (parameters determine learning rate for chosen and unchosen actions, respectively)

        al = curr_params(1);
        ga = curr_params(2);
% %         ga = al;
        
        idxChosen   = choice_own(iTrial);
        idxUnchosen = 1:nActions;
        idxUnchosen(idxChosen) = [];
        pi_potential = varargin{1}(iTrial,:); % score_potential_own
        f_mat_own(iTrial,idxChosen)   = (1-al) * f_mat_own(max(1,iTrial-1),idxChosen)   + al .* pi_potential(idxChosen); 
        f_mat_own(iTrial,idxUnchosen) = (1-ga) * f_mat_own(max(1,iTrial-1),idxUnchosen) + ga .* pi_potential(idxUnchosen); % same decay, but different responsivity to reward
        
        idxChosen   = choice_other(iTrial);
        idxUnchosen = 1:nActions;
        idxUnchosen(idxChosen) = [];
        pi_potential = varargin{2}(iTrial,:); % score_potential_other
        f_mat_other(iTrial,idxChosen)   = (1-al) * f_mat_other(max(1,iTrial-1),idxChosen)   + al .* pi_potential(idxChosen); 
        f_mat_other(iTrial,idxUnchosen) = (1-ga) * f_mat_other(max(1,iTrial-1),idxUnchosen) + ga .* pi_potential(idxUnchosen); 

    case 'seq_own' % sequencer finding pattern in *one* player
        
        % tends to repeat choice sequences of length x+1 (a free parameter), or 
        % exploit those in the opponent; i.e. code tries to find historical copies 
        % of the actions of the last x trials and takes the next action as prediction
        
        % this implementation takes into account _all_ matches (not just the most
        % recent one), and correspondingly predicts a whole distribution (rather 
        % than just a point estimate)
        
        % takes them into account with an exponentially decaying memory weight
        % -> if decay_rate = 1: whole distribution, no decay
        % -> if decay_rate = 0: i.e. only most recent match
        
        % when there's no match, responds according to sequence_length = 0
        % (i.e. to whole historic distribution)
        
        pattern_length = curr_params(1);
        decay_rate     = curr_params(2);
        idx_pattern = iTrial - pattern_length + 1;
        
        pattern_length_used = pattern_length;
        if pattern_length ~= 0
            idx_matches = strfind(choice_own(1:iTrial)',choice_own(max(1,iTrial-pattern_length+1):iTrial)');
            if sum(idx_matches < idx_pattern) < 2
                pattern_length_used = 0;
                idx_matches = 1:iTrial+1; % if not enough matches, fall back to sequence length = 0 strategy, i.e. mem_decay
            end
        else
            idx_matches = 1:iTrial+1; % because below -1 to exclude the self-match
        end
            
        idx_pred = idx_matches(1:end-1) + pattern_length_used;
        predictions = choice_own(idx_pred);  
        weights = decay_rate .^ (iTrial - idx_pred);
        p_own = NaN(nActions,1);
        for iAction = 1:nActions
            p_own(iAction) = sum(weights(predictions == iAction));
        end
        f_mat_own(iTrial,:) = p_own ./ sum(p_own);
        
        pattern_length_used = pattern_length;
        if pattern_length ~= 0
            idx_matches = strfind(choice_other(1:iTrial)',choice_other(max(1,iTrial-pattern_length+1):iTrial)');
            if sum(idx_matches < idx_pattern) < 2
                pattern_length_used = 0;
                idx_matches = 1:iTrial+1; % if not enough matches, fall back to sequence length = 0 strategy, i.e. mem_decay
            end
        else
            idx_matches = 1:iTrial+1; % because below -1 to exclude the self-match
        end
            
        idx_pred = idx_matches(1:end-1) + pattern_length_used;
        predictions = choice_other(idx_pred);  
        weights = decay_rate .^ (iTrial - idx_pred);
        p_own = NaN(nActions,1);
        for iAction = 1:nActions
            p_own(iAction) = sum(weights(predictions == iAction));
        end
        f_mat_other(iTrial,:) = p_own ./ sum(p_own);
                
    case 'seq_both' % sequence learner *common history*
        
        % same as seq_own, but tends to repeat sequences of choice _combinations_
        % of own choices AND opponent choices
        
        pattern_length = curr_params(1);
        idx_pattern = iTrial - pattern_length + 1;
        
        hist_both_own = varargin{1};
% %         hist_both_own(end+1) = 10 * choice_other(iTrial) + choice_own(iTrial); % done in initialization
        idx_matches = strfind(hist_both_own(1:iTrial)',hist_both_own(max(1,iTrial-pattern_length+1):iTrial)');
        if any(idx_matches < idx_pattern)
            idx_latest_match = max(idx_matches(idx_matches < idx_pattern));
            prediction = floor(hist_both_own(idx_latest_match + pattern_length)/10);
            f_mat_own(iTrial,:) = zeros(1,nActions);
            f_mat_own(iTrial,prediction) = 1;
        else
            f_mat_own(iTrial,:) = repmat(1/nActions,1,nActions);
        end
        
        hist_both_other = varargin{2};
% %         hist_both_other(end+1) = 10 * choice_own(iTrial) + choice_other(iTrial);
        idx_matches = strfind(hist_both_other(1:iTrial)',hist_both_other(max(1,iTrial-pattern_length+1):iTrial)');
        if any(idx_matches < idx_pattern)
            idx_latest_match = max(idx_matches(idx_matches < idx_pattern));
            prediction = floor(hist_both_other(idx_latest_match + pattern_length)/10);
            f_mat_other(iTrial,:) = zeros(1,nActions);
            f_mat_other(iTrial,prediction) = 1;
        else
            f_mat_other(iTrial,:) = repmat(1/nActions,1,nActions);
        end
        
end
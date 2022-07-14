function p_actions = tomRL_responseFunc(probabilities,params,type)

switch type
    
    case 'argmax'
        [~,idx] = max(probabilities);
        p_actions = zeros(size(probabilities));
        p_actions(idx) = 1;
        
    case 'softmax'
        beta = params;
        p_actions = exp(beta*probabilities)/(sum(exp(beta*probabilities)));

% or, if ignoring noise in the updating process
% p_actions = exp(probabilities)/(sum(exp(probabilities)));

end

end
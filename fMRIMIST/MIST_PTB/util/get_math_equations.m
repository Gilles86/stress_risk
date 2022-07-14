%% generate math problems

get_equation=0;
end_result = randi(10)-1;

while ~get_equation
   
    % numbers:
    nums = randi(20, [1,eq_length]);
    
    % operations
    ops = randi(op_length, [1,eq_length-1]);
    % 1 +
    % 2 -
    % 3 *
    % 4 /
    result = nums(1);
    equation_text = num2str(nums(1));
    for n = 2 :length(nums)
        if ops(n-1) == 1
            result = result + nums(n);
            equation_text = [equation_text, ' + ', num2str(nums(n))];
        elseif ops(n-1) == 2
            result = result - nums(n);
            equation_text = [equation_text, ' - ', num2str(nums(n))];
        elseif ops(n-1) == 3
            result = result * nums(n);
            if n ==2
                equation_text = [equation_text, ' * ', num2str(nums(n))];
            else
                equation_text = ['(',equation_text, ') * ', num2str(nums(n))];
            end
            
        elseif ops(n-1) == 4
            result = result / nums(n);
            if n ==2
                equation_text = [equation_text, ' / ', num2str(nums(n))];
            else
                equation_text = ['(',equation_text, ') / ', num2str(nums(n))];
            end
            
        end
        
    end
    equation_text = [equation_text, ' = '];
    if end_result >= 0 && end_result < 10 && end_result == round(end_result) && end_result == result
        get_equation = 1;
    end
    
    
    
end
% 


    
    
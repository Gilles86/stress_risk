clear all

rng('shuffle')

subs = 50;
sessions = 2;

conditions = [ones(25,1) zeros(25,1)];
conditions = [conditions; [zeros(25,1) ones(25,1)]];
%
subIDS = randperm(50)';


permuted = conditions(subIDS,:);

permuted = [[1:50]'    permuted];

permuted = sortrows(permuted,1,"ascend");

T = array2table(permuted,'VariableNames',{'SUBID', 'CondSesh1', 'CondSesh2'});





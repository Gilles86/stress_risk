clear all

mu1    = 1;
sigma1 = 1; % distribution of risk preferences
%rho is auto-correlation of measurements
%N = 50;

effect = .3; %mean change of stress
%sigma_effect = .01; % sd of change in stress
%stress_effect = mean_effect + sigma_effect.*randn(N,1);

% column 1 is pre column 2 is post



for jj = 1:10

    N = jj *10;

    ii = 1;
    for rho = .25:.3:.85

        [ pwr_between(jj,ii) pwr_PrePost(jj,ii) pwr_Repeated(jj,ii) ] = func_power(mu1, sigma1, rho , N, effect);

        ii = ii + 1;
    end

end
%
p = plot(10:10:100,pwr_PrePost,'-',10:10:100,pwr_between,'--', 10:10:100,pwr_Repeated,'-.');


legend({'PrePost: rho=.25' 'PrePost: rho=.55' 'PrePost: rho=.85' 'OnlyBetween: rho=.25' 'OnlyBetween: rho=.55' 'OnlyBetween: rho=.85' ...
        'Repeated measures: rho=.25' 'Repeated measures: rho=.55' 'Repeated measures: rho=.85' })
title(['Power for mean-diff = ' num2str(effect)])
xlabel('Sample Size')
ylabel('Power')
grid on
p(1).LineWidth = 2;
p(2).LineWidth = 2;
p(3).LineWidth = 2;
p(4).LineWidth = 2;
p(5).LineWidth = 2;
p(6).LineWidth = 2;












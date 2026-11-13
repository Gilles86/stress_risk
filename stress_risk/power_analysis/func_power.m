function [ pwr_between pwr_PrePost pwr_Repeated] = func_power(mu1, sigma1, rho , N, effect )

rng("shuffle")
for ii = 1:1000

    samples_stress = mvnrnd([ mu1 mu1 ],[ sigma1 rho ; rho sigma1 ],N);
    samples_control = mvnrnd([ mu1 mu1 ],[ sigma1 rho ; rho sigma1 ],N);

    samples_stress(:,2) = samples_stress(:,2) + effect;

    H_Between(ii,1)  = ttest2(samples_stress(:,2),samples_control(:,2));
    H_PrePost(ii,1)  = ttest2(samples_stress(:,2)-samples_stress(:,1),samples_control(:,2)-samples_control(:,1));

    H_Repeated(ii,1)  = ttest(samples_stress(:,1), samples_stress(:, 2));
end

pwr_between = mean(H_Between);
pwr_PrePost = mean(H_PrePost);
pwr_Repeated= mean(H_Repeated);

end
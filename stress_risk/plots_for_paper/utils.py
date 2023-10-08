import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as ss

x = np.linspace(0, 10, 1000)
x = np.linspace(1.0, 9., 1000)

def get_posterior(mu1, sd1, mu2, sd2):
    var1, var2 = sd1**2, sd2**2
    return mu1 + (var1/(var1+var2))*(mu2 - mu1), np.sqrt((var1*var2)/(var1+var2))

def plot_dist(mu, sd, y=0.0, color=None, shade=True, **kwargs):

    p = ss.norm(loc=mu, scale=sd).pdf(x)
    p /= p.max() / .65

    plt.plot(x, y+p, color=color, **kwargs, alpha=.8)

    if shade:
        plt.fill_between(x, y, y+p, alpha=0.3, color=color)

    sns.despine()


def plot_bayesian_inference(risky_first,base, frac=0.55,
                            common_prior = False,
                            palette = sns.color_palette('coolwarm', 4)[::-1]):
    #priors
    base_n = [5,7,10,14,20,27]
    mu_prior_safe, std_prior_safe = np.log(np.mean(base_n)), .75
    mu_prior_risky, std_prior_risky = np.log(np.mean(np.array(base_n)/0.55)), .75 # np.log(np.mean(base_n))* 1.55

    # evidence_std
    sd_ev_1st = 0.5
    sd_ev_2nd = 0.1
    std_evidence_risky = sd_ev_1st if risky_first else sd_ev_2nd
    std_evidence_safe = sd_ev_1st if risky_first == False else sd_ev_2nd

    mu_evidence_risky = np.log(base/frac)
    mu_evidence_safe = np.log(base)

    #posteriors
    mu_posterior_risky, std_posterior_risky = get_posterior(mu_evidence_risky, std_evidence_risky, mu_prior_risky, std_prior_risky)
    mu_posterior_safe, std_posterior_safe = get_posterior(mu_evidence_safe, std_evidence_safe, mu_prior_safe, std_prior_safe)

    #first
    mu_evidence_first = mu_evidence_risky if risky_first else mu_evidence_safe
    col_first = palette[0] if risky_first else palette[3]
    plot_dist(mu_evidence_first, sd_ev_1st, 0, color=col_first) # y=0.0 by default = height !
    plt.plot([mu_evidence_first, mu_evidence_first], [0.0, -2.], ls='--', c=col_first) #straight lines down

    #second 
    mu_evidence_second = mu_evidence_safe if risky_first else mu_evidence_risky
    col_sec = palette[3] if risky_first else palette[0]
    plot_dist(mu_evidence_second, sd_ev_2nd,  -1.0, color=col_sec)
    plt.plot([mu_evidence_second, mu_evidence_second], [-1, -2.], ls='--', c=col_sec)
    
    #priors
    y_safe = -1 if risky_first else 0
    y_risky = 0 if risky_first else -1
    plot_dist(mu_prior_safe, std_prior_safe, y_safe, color=palette[2])
    plot_dist(mu_prior_risky, std_prior_risky,y_risky, color=palette[1])

    # bayesian inference
    plot_dist(mu_posterior_risky, std_posterior_risky, -2.0, color=palette[0]) # risky
    plot_dist(mu_posterior_safe, std_posterior_safe, -2.0, color=palette[3]) # safe

    # arrows
    plt.annotate('', xytext=(mu_evidence_safe, -2), xy=(mu_posterior_safe, -2), arrowprops={"facecolor":palette[3], 'edgecolor':'k', "linewidth":1., 'shrink':0.05, 'headlength':6})
    plt.annotate('', xytext=(mu_evidence_risky, -2), xy=(mu_posterior_risky, -2), arrowprops={"facecolor":palette[0], "linewidth":1., 'edgecolor':'k', 'shrink':0.05, 'headlength':6})

    # draw the 4 lines 
    for ix in range(4):
        plt.plot([1,7], [-ix, -ix], c='gray', ls='-') # np.log(90)

    # EV
    post_ev_norm_safe = mu_posterior_safe #post_ev_norm_safe * (7/100) + 1
    post_ev_norm_risky = mu_posterior_risky + np.log(0.55) #post_ev_norm_risky * (7/100) + 1

    plt.scatter([post_ev_norm_safe], [-3.], color=palette[3], zorder=10) # dots
    plt.scatter([post_ev_norm_risky], [-3.], color=palette[0], zorder=10)
    plt.plot([mu_posterior_safe, post_ev_norm_safe], [-2, -3], color=palette[3]) # lines connecting with aboove
    plt.plot([mu_posterior_risky, post_ev_norm_risky], [-2, -3], color=palette[0])

    if  post_ev_norm_safe > post_ev_norm_risky: #mu_posterior_safe >  mu_posterior_risky*.55:
        plt.gca().annotate('EV[risky] < EV[safe]', (3.25, -3.15),  ha='center', va='top')
    else:
        plt.gca().annotate('EV[safe] < EV[risky]', (3.25, -3.15),  ha='center', va='top')

    plt.xlim(0,5)
    plt.axis('off')


def annotat_bayesian_inference():
    plt.gca().annotate('1st option', (.75, 0.0), ha='right', va='center')
    plt.gca().annotate('2nd option', (0.75, -1.0), ha='right', va='center')
    plt.gca().annotate('Bayesian inference \n log space ', (0.75, -2.0), ha='right', va='center')
    plt.gca().annotate('Expected value \n natural space', (0.75, -3.0), ha='right', va='center')

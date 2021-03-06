title: Why Multi-armed Bandit algorithms are superior to A/B testing
date: 2012-06-03 10:00
author: Chris Stucchio
tags: algorithms, bandit algorithms, ab testing
category: bandit algorithms





In a recent [post](http://visualwebsiteoptimizer.com/split-testing-blog/multi-armed-bandit-algorithm/), a company selling A/B testing services made the claim that A/B testing is superior to [bandit algorithms](https://en.wikipedia.org/wiki/Multi-armed_bandit). They do make a compelling case that A/B testing is superior to one particular [not very good](http://stevehanov.ca/blog/index.php?id=132) bandit algorithm, because that particular algorithm does not take into account statistical significance.

However, there are bandit algorithms that account for statistical significance.

**UPDATE:** Several years after writing this post, I've learned that it's a bit misunderstood. After reading this post, please go read [this followup post](/blog/2015/dont_use_bandits.html) to avoid any misconceptions.

# Simple algorithms

To begin, let me discuss the simple algorithms, namely epsilon-greedy ("20 lines of code that will beat A/B testing every time") and epsilon-first (A/B testing).

An important disclaimer: *I'm glossing over a lot of math to simplify this post*. The target audience of this post is web programmers, not mathematicians.

## Epsilon-greedy algorithms

The original [post](http://stevehanov.ca/blog/index.php?id=132) described an epsilon-greedy algorithm:

    inputs:
        machines :: [ GamblingMachine ]
	num_plays :: Map(GamblingMachine -> Int)
        total_reward :: Map(GamblingMachine -> Float)

    select e // In the original post, e = 0.1
    while True:
        x <- UNIFORM([0,1]) // A uniformly distributed random variable
	if x < e: //exploration phase
	    let m = random_choice(machines)
	    reward <- play_machine( m )
	    num_plays[m] += 1
	    total_reward[m] += reward
	else: //exploitation phase
	    average_rewards = Map( (m, total_reward[m] / num_plays[m]) for m in machines )
	    best_machine = argmax( average_rewards ) //Find the machine with the highest reward
	    reward <- play_machine( best_machine )
	    num_plays[best_machine] += 1
	    total_reward[best_machine] += reward

Basically, exploration with probability `e` and explotation with probability `1-e`.

This is not a good algorithm. Consider the scenario of two machines - machine A has reward 1, machine B has reward 0. Even after the epsilon-greedy algorithm has converged, 10% of the time a random machine will be chosen. So given "convergence", the odds of choosing machine B are still:

    P( exploration) * P(machine B | exploration) = e * (1/2)

So your total reward can be at most:

    num_plays * (1 - e/2)

I.e., if `e=0.1` (as advocated in the original blog post), you are leaving $5 on the table for every $100 you could potentially earn.

## A/B testing or Epsilon-first algorithms

The approach that Visual Website Optimizer advocates is A/B testing, which is called epsilon-first in the formal literature. The way it works is that you explore for a finite number of plays (the A/B test) and exploit forever after:

    for i in 1...N:
        m <- choose_machine // Can be done at random, i % num_machines, etc
	reward <- play_machine( m )
	save_results(m, reward, i)

    best_machine_estimate = statistical_test( N, reward_history )

    while True:
        play_machine( best_machine_estimate )

I won't get into the specifics of how Visual Website Optimizer set up their A/B test, since *they did it wrong* (see their [code](http://pastie.org/4007859)). In particular, what they did is A/B testing with repeated peeks - they measured statistical significance repeatedly throughout the A/B test. Rather than explaining why this is wrong, I'll just refer to the excellent post [How Not to Run an A/B Test](http://www.evanmiller.org/how-not-to-run-an-ab-test.html), by Evan Miller. Seriously, go read that article.

The key point in understanding epsilon-first algorithms is recognizing that `statistical_test` has an error rate (which is dependent on `N` as well as the prior distribution of machine rewards). Rather than getting into the details of statistical testing, I'll just make up a symbol for it, `Err`.

Let us now suppose the epsilon-first algorithm has finished the exploration phase. In that case:

    P( best_machine_estimate == true_best_machine ) = 1 - Err

Suppose again that `true_best_machine` has reward 1, and the other worse machines all have reward 0. Then in the exploitation phase, your reward is:

    num_plays x P( best_machine_estimate == true_best_machine) = num_plays x (1 - Err)

If you run your A/B tests with 5% confidence levels (as most people do), you are again leaving $5 on the table for every $100 you could earn.

In the epsilon-greedy case, the most likely scenario is that you collect $95/$100. In the epsilon-first case, the most likely scenario is that you collect $100, and there is a 5% chance you collect $0. But in both cases, you are leaving money on the table.

# UCB1 - A superior bandit algorithm

I'll now discuss a somewhat more complicated algorithm. It's taken from the paper [Finite-time Analysis of the Multiarmed Bandit Problem](http://homes.dsi.unimi.it/~cesabian/Pubblicazioni/ml-02.pdf), by Auer, Cesa-Bianchi and Fischer, Machine Learning, 47, 235-256, 2002.

The algorithm is called UCB1, and it's based on the following idea. Figure out which machine *could* be the best possible one (based on your statistical level of confidence), and play that machine as much as possible. Note that I didn't say which machine *is* the best, but which one *could* be the best.

There are two ways a machine *could* be the best:

1. You have measured it's mean payout to be higher than all the others, and you are certain of this with a high degree of statistical significance.
2. You have not measured it's mean payout very well, and the confidence interval is large.

The algorithm is based on the Chernoff-Hoeffding bound. Suppose we have a random generator `rand`. Repeated calls to `rand` are assumed to be independent of each other, and it's range is bounded:

    x <- rand
    assert(0 <= x && x <= 1)

Now suppose we run `N` trials and compute the average:

    avg = 0
    for i in 1..N:
        avg += rand
    avg /= N

Define `m` to be the theoretical statistical mean of `rand` (i.e., if `rand` were a fair coin flip, `m=0.5`). Then `avg` is an approximation to `m`.

Chernoff-Hoeffding says that for any `a > 0`, we have the following bound:

    P( avg > m + a) <= 1 / exp(2 * a^2 N)

I.e., the probability that `avg` overestimates `m` by at least `a` decreases exponentially with `N`. This is just a way of quantifying something we already know intuitively - the more trials we run, the better our estimate of the mean of a random variable.

If we reverse Chernoff-Hoeffding and do some arithmetic (which is already done in the [paper](http://homes.dsi.unimi.it/~cesabian/Pubblicazioni/ml-02.pdf), so I won't repeat it here), we can get the following *stylized fact* (i.e., it isn't true, but is intuitively useful):

    true_mean(m) <= avg[m] + sqrt( 2 ln(N) / num_plays[m] )

Here `m` is a machine, `avg[m]` the average reward observed so far from machine `m`, `num_plays[m]` the number of times machine `m` has been played, and `N` the total number of plays across *all machines*. From here on out, I'll refer to `sqrt( 2 ln(N) / num_plays[m] )` as the *confidence bound*.

Finally, the algorithm `UCB1` is as follows:

    Play each machine once.

    while True:
        best_possible_true_mean = { m -> avg[m] + sqrt( 2 ln(N) / num_plays[m] ) }
            // This is pseudocode for a "dict comprehension"
            // I.e. best_possible_true_mean[m] = avg[m] + ...
            to_play = argmax(best_possible_true_mean)
            reward <- play_machine(to_play)

            update avg[to_play], num_plays[m], N

This algorithm starts off in a pure exploration phase, since `avg[m]` will be small compared to the confidence bound. For example, with `N=10` and `num_plays[m]=5`, we find that the confidence bound is 0.9597. For comparison, `avg[m]` is some number bounded by 1.

However, for larger values of `N`, `ln(N)` grows very slowly, and eventually `ln(N) / num_plays[m]` will become small. With `N=400` and `num_plays[m]=200`, we find the confidence bound has dropped to 0.2447. If `avg[m_best] = 0.50` and `avg[m_worst] = 0.20`, the algorithm will start playing `m_best` most of the time.

At this point, `N` and `num_plays[m_best]` are increasing, but `num_plays[m_worst]` is remaining constant. This means the confidence bound for `m_worst` is slowly increasing. At `N=8000`, the confidence bound on the worst machine is 0.2997, while the confidence bound on the best is only 0.04800. We will continue playing machine `m_best` for a while. For simplicity, I'll assume `avg[m_best]=0.5` and `avg[m_worst]=0.2` on *every play*. (In reality this won't be true, I'm just trying to illustrate a point here.)

    N = 5000
    avg[m_best] + sqrt(2*ln(N)/num_plays[m_best]) = 0.5596
    avg[m_worst] + sqrt(2*ln(N)/num_plays[m_worst]) = 0.4918

    N = 9000
    avg[m_best] + sqrt(2*ln(N)/num_plays[m_best]) = 0.5455
    avg[m_worst] + sqrt(2*ln(N)/num_plays[m_worst]) = 0.5017

    N=25000
    avg[m_best] + sqrt(2*ln(N)/num_plays[m_best]) = 0.5286
    avg[m_worst] + sqrt(2*ln(N)/num_plays[m_worst]) = 0.5182

    N = 36422
    avg[m_best] + sqrt(2*ln(N)/num_plays[m_best]) = 0.52408152492
    avg[m_worst] + sqrt(2*ln(N)/num_plays[m_worst]) = 0.524082215906

At N=36422, we will play machine `m_worst` once. Now `num_plays[m_worst]=201`. And at this point, we go back to playing machine `m_best`:

    N = 36423
    avg[m_best] + sqrt(2*ln(N)/num_plays[m_best]) = 0.5240815563951478,
    avg[m_worst] + sqrt(2*ln(N)/num_plays[m_worst]) = 0.5232754585667818

The key point here is that `ln(N)` grows very slowly relative to `num_plays[m_worst]`. So while the exploration process continues forever, the fraction of time we spend exploring decreases exponentially.

Another important fact is that the exploration time is adaptive - if `avg[m_best]` and `avg[m_worst]` are very close together (i.e., 0.5 and 0.51), then we will spend more time exploring until we are finally confident of which machine is the best one.

There is a theorem proven in the [paper](http://homes.dsi.unimi.it/~cesabian/Pubblicazioni/ml-02.pdf) which says that the regret of this algorithm grows only logarithmically. This means that your reward will be proportional to:

    num_plays - log(num_plays)

This value will *always* be larger than either `num_plays * (1-e/2)` or `num_plays * (1 - Err)` provided `num_plays` is sufficiently large.

This means that UCB1 will always beat both A/B testing and "20 lines of code...". (Though actually, UCB1 will take only marginally more than 20 lines of code.)

# Conclusion

If you don't do any of this stuff (A/B, epsilon-greedy, MAB), pick whichever one is easiest and do it. Any of these fine optimization methods are *vastly* better than nothing. If you really want to be optimal, try UCB1 or any of the more modern adaptive bandit methods. They are marginally better than A/B tests.

I've also written quite a bit more on bandit algorithms since this post was published. I've described my favorite bandit algorithm, the [Bayesian Bandit](/blog/2013/bayesian_bandit.html), which achieves similar accuracy to UCB1. I wrote this blog post about [Bayesian A/B testing](http://www.bayesianwitch.com/blog/2014/bayesian_ab_test.html). And I wrote a post about measuring a [changing conversion rate](/blog/2013/time_varying_conversion_rates.html), which (when combined with the [Bayesian Bandit](/blog/2013/bayesian_bandit.html)) can handle the case of time varying conversion rates.

**UPDATE:** Several years after writing this post, I've learned that it's a bit misunderstood. After reading this post, please go read [this followup post](/blog/2015/dont_use_bandits.html) to avoid any misconceptions.

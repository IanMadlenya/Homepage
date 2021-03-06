title: The Adversarial Bandit is not a Statistics Problem
date: 2014-02-24 09:00
author: Chris Stucchio
tags: statistics, bandit algorithms, adversarial bandit, game theory
mathjax: true
category: bandit algorithms





In the past couple of weeks, the excellent article [A Fervent Defense of Frequentist Statistics](http://lesswrong.com/lw/jne/a_fervent_defense_of_frequentist_statistics/) has been making the rounds. The article makes some strong arguments in favor of using frequentist tools, since many of them are more computationally efficient than Bayesian methods.

However, the author makes a fundamental mistake. While describing Myth 5, he points out that Frequentist methods can handle all sorts of odd cases, including the adversarial bandit problem. This is a rather odd claim to make, given that the adversarial bandit problem is not a statistics problem at all. Rather, the adversarial bandit is a problem of game theory - how do you behave in order to defeat an omniscient adversary?



# The Adversarial Bandit

The adversarial bandit problem is an odd one. It's fundamentally a game with two players - the *bandit* and *god*.

The game is turn-based, and at each turn, the player must pull the lever on one of a set of `M` slot machines. At time $@ t $@, the $@ i'th$@ slot machine pays out a rewards of $@ x_i(t) $@. So if the player made the sequence of choices $@ i(t) $@, then the bandit's reward is

$$ G(T) = \sum_{t=0}^T x_{i(t)}(t) $$

The other player in this game is god. In this game god is somewhat omnipotent - he is in complete control of $@ x_i(t)$@. He can allow the rewards to be anything he wants - the only thing he cannot do is alter $@ x_i(t) $@ *after* the player has already pulled the lever on the machine.

In this game, god doesn't like the bandit. God's goal is to make the bandit feel bad about having a reward which is lower than he might otherwise desire. In one formulation, god's goal is to maximize the players *weak regret*:

$$ \textrm{Weak Regret} = \left( \max_i \sum_{t=0}^T x_i(t) \right) - G(T)$$

This is the difference between amount the bandit *could have won* if he simply chose the best slot machine to play from the beginning, and the amount he actually won. In another formulation, god's goal is to maximize total regret:

$$ \textrm{Regret} = \left( \max_{j(t)} \sum_{t=0}^T x_{j(t)}(t) \right) - G(T)$$

This is the difference between what the bandit could have won if he chose the *best strategy* and what he actually did win.

In contrast, the player's goal is to minimize the total regret.

# God is Omniscient

An important fact about this game is that god is omniscient. He knows the strategy the player is running and has the computational resources to mentally run this strategy himself. This means he can predict the player's actions. In contrast, the bandit has no ability to predict the actions of god.

So now let us suppose that the bandit has constructed a strategy $@ i(t) $@ which he believes is optimal. God knows this strategy. So god can choose the $@ x_{i}(t) $@ values in such a way as to maximize the reget.

Due to the omniscience of god, this is actually a pretty boring game. God can counter any strategy simply by predicting one step ahead of the bandit.

## A deterministic puzzle

The other important fact about the adversarial bandit is that *there is no uncertainty*. There is no need to estimate unknown parameters of any probability distribution, or to compute a posterior, because *there is no probability distribution*.

This is very different from stochastic bandit problems. In stochastic bandit problems, there are probability distributions to estimate and posteriors to compute. Stochastic bandits are a statistics problem. The adversarial bandit, in contrast, is a deterministic game theory problem.

The flaw in the [Fervent Defense](http://lesswrong.com/lw/jne/a_fervent_defense_of_frequentist_statistics/) blog post is that it is defining Frequentist methods as the complement of Bayesian methods. But this is a fallacy - by this logic, solving the wave equation is a Frequentist model of electromagnetism. But that's just silly - much like the adversarial bandit, the problem of wave propagation is neither frequentist nor bayesian. It's simply not a statistics problem.

# Reducing the advantage of intelligence

If you have a superintelligent opponent, or an opponent with secret knowledge that you do not have, your best hope is simply to reduce the advantage that their intelligence provides.

For example, if you are a navy and your opponent has cracked your transmission code, it's difficult to come up with a good strategy for your submarines. If you order your submarines to attack ship A rather than B, your opponent will send their destroyers to protect ship A. The same will happen if you order your submarine to attack ship B - they will observe that message and defend B accordingly.

To counteract your opponents informational advantage, all you can do is construct a world where an information advantage is useless. For example, instead of telling your submarine which ship to attack, you simply tell them to attack ships at random. Now your opponents ability to tap into your communications network has been rendered useless.

This is the basic idea behind the [EXP3 algorithm](http://jeremykun.com/2013/11/08/adversarial-bandits-and-the-exp3-algorithm/) which has been proposed as a "solution" to the problem of adversarial bandits. Rather than deterministically choosing which slot machine to play, the bandit uses a random number generator (weighted based on the history of the reward sequence) to break god's information advantage. By choosing randomly, god cannot make the bandit's next move the worst possible one since god doesn't know the bandit's next move.

In a purely random world, information is useless. The EXP3 algorithm merely postulates a world which is sufficiently random so that god's information advantage is partially neutralized, but sufficiently deterministic so that the bandit can still predict the superior arm most of the time.

## A weird assumption

Tangentially, it's completely unclear to me why god is able to predict the bandit's deterministic plans, but unable to predict the outcome of the bandit's pseudo random number generator. It seems to me that if god can predict the outcome of `com.bandit.Strategy.predict()`, then god should also be able to predict the outcome of `java.util.Random.nextDouble`.

# A poor model of the world

Fundamentally the adversarial bandit is a thought experiment. Many other bandit algorithms, for example UCB1 and the [Bayesian Bandit](/blog/2013/bayesian_bandit.html), come with strong assumptions - a typical assumption is that the conversion rate of each variant does not change with time. That's a very unrealistic assumption.

So in order to build a better model, some math lovers decided to come up with the weakest assumption they could think of that would still get results. The adversarial bandit is the result of that process. But the adversarial bandit models an adversarial world - this is very different from an *indifferent* world where the outcome of each slot machine varies with time. In an adversarial world, people will stop clicking on ads about beanie babies just to spite me - in an indifferent world, they will stop clicking on them simply because they have fallen out of favor.

In an adversarial world, using a deterministic algorithm will actually *change the world*. In an indifferent world, it will not. A bandit algorithm in an indifferent world is a statistics problem - your goal is to describe the world with a probability distribution and make decisions based on the result. In an adversarial world it's a game theory problem.

The fact that Bayesian Statistics don't apply to deterministic game theory does not make game theory a problem of frequentist statistics - it just means there are areas of math that are not statistics at all.

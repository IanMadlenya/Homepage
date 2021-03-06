title: How to lie without statistics - ProPublica edition
date: 2016-05-24 10:00
author: Chris Stucchio
tags: bias detection, frequentist statistics, statistics
mathjax: true
nolinkback: true

![almost statistically significant](/blog_media/2016/propublica_is_lying/p_values.png)

I've recently discovered a 4 step process for lying without statistics. Here it is:

1. Write down the conclusion.
2. Run a statistical analysis.
3. If the statistical analysis agrees with your conclusion, publish it.
4. If the statistical analysis disagrees with your conclusion, write some anecdotes and allude to the fact that you did statistics. Don't mention your actual results.

Can this process work? Won't the kind readers notice? Apparently not. ProPublica's [dishonest and misleading article](https://www.propublica.org/article/machine-bias-risk-assessments-in-criminal-sentencing) about bias in criminal justice has been taking the internet by storm. Let me get into mathematical detail.

## Background: how to look for bias

In a previous post I described a [method of analyzing whether an algorithm is biased](https://www.chrisstucchio.com/blog/2016/alien_intelligences_and_discriminatory_algorithms.html). The method, described loosely, is as follows.

Take a predictor which you suspect might be biased against some group - say blacks. This predictor is designed to predict some output data. A simple way to measure whether this predictor biased is to build a *new* predictor taking both the old predictor and the (potentially) biasing variable as an input. You'll basically build a new data set as follows:

```python
    data[:,0] = old_predictor
    data[:,1] = is_black
```

Then you build a new predictor by running linear regression or some similar statistical model on this new data set. I'll illustrate with linear regression.

The new predictor will be:

```python
def new_predictions(new_data):
    return new_data[:,0] * alpha[0] + new_data[:,1] * alpha[1]
```

The predictor `alpha` can be found by linear regression or some similar thing. For more detail on this, please go see [my previous post](https://www.chrisstucchio.com/blog/2016/alien_intelligences_and_discriminatory_algorithms.html) on the topic, specifically the "What if measurements are biased" section.

Lets consider intuitively two possibilities.

1. If the old predictor is unbiased, then you'll discover that the new predictor is identical to the old one. This means that the best possible predictor is, in fact, the old predictor. The vector `alpha` is then approximately `[1,0]` (modulo statistical noise and a normalizing constant).
2. If the old predictor is biased, you'll discover that the new predictor combines the old predictor with an unbiasing factor to build a better predictor. I.e., you'll get `alpha = [0.8, 0.2]` or something like that.

In short, the size of the second coefficient (relative to the first) is directly proportional to the degree to which the old predictor was biased. Here's a concrete example using synthetic data:

```python
ability = norm(0,1).rvs(N) #The true driver
is_black = bernoulli(0.1).rvs(N) #Some people are black

data = zeros(shape=(N,nvars), dtype=float)

data[:,0] = 0.5*ability[:] + norm(0,1).rvs(N) # An old predictor, which is kind of good.
data[:,0] -=  0.5*is_black # But lets put in some bias!
data[:,1] = is_black

output = ability + norm(0,1).rvs(N)

alpha = lstsq(data, output)[0]
```

When you run this analysis, you get something along the lines of `alpha=[ 0.39471238,  0.20973444]`. (Your numbers may vary due to random sampling.) The new predictor cancels out the biases in the old predictor with the `alpha[1]` term.

In contrast, if you remove the bias from the predictor (by deleting `data[:,0] -= 0.5*is_black`), the result is `alpha=[ 0.52380874,  0.03915861]`. There is no bias, so the new predictor is basically just the same as the old one.

In short, this procedure of building a new predictor out of the old predictor plus a biasing variable is a recipe for us to find bias. If bias is present, the second term will be statistically significantly different from zero. If it's absent, it won't. I'm glossing over the details of the statistical test (i.e., how to determine whether 0.0391 is significant or not, but that's the general idea.

### Is the predictor good?

The other useful question that this procedure can answer is whether or not the predictor is actually good. If the coefficient on the old predictor (in this case `alpha[0]`) is small, that means the predictor is not usefully correlated with the output in question. In contrast, if `alpha[0]` is large, then the predictor is doing a good job of predicting outcomes. Again, some sort of statistical test should be run to determine what "small" and "large" mean.

## ProPublica's analysis

ProPublica ran the exact analysis I describe above. The main difference is that they used a [Cox model](https://en.wikipedia.org/wiki/Proportional_hazards_model) for survival probabilities (i.e., the probability of a criminal *not* re-offending) rather than linear regression. The general idea is similar but the the functional form differs. From what I can tell this is the right thing to do.

Here's their [analysis](https://github.com/propublica/compas-analysis/blob/master/Compas%20Analysis.ipynb). Lines [36] and [46] are the key here. Unlike me in this blog post, they didn't gloss over the statistical test - instead, the used the one that came built into R.

The relevant (bias factor) terms are `race_factorAfrican-American:score_factorHigh`, `race_factorAfrican-American:score_factorMedium`, etc.

    race_factorAfrican-American                     4.586 4.52e-06 ***
    race_factorAsian                               -1.548   0.1217
    race_factorHispanic                            -0.657   0.5114
    race_factorNative American                     -1.253   0.2101
    race_factorOther                                0.128   0.8978
    score_factorHigh                               15.358  < 2e-16 ***
    score_factorMedium                             11.801  < 2e-16 ***
    race_factorAfrican-American:score_factorHigh   -1.900   0.0574 .
    race_factorAsian:score_factorHigh               1.712   0.0869 .
    race_factorHispanic:score_factorHigh           -0.601   0.5480
    race_factorNative American:score_factorHigh     1.805   0.0710 .
    race_factorOther:score_factorHigh               1.599   0.1098
    race_factorAfrican-American:score_factorMedium -1.897   0.0578 .
    race_factorAsian:score_factorMedium             1.388   0.1653
    race_factorHispanic:score_factorMedium          0.398   0.6908
    race_factorNative American:score_factorMedium   1.240   0.2148
    race_factorOther:score_factorMedium            -1.440   0.1498

This analysis leads us to three conclusions:

1. The predictor - namely `score_factorHigh` and `score_factorMedium` is highly statistically significant - the p-value is nearly zero. Cool, looks like the predictor actually does a good job.
2. The predictor is probably not biased against any particular race - the `race_factorAfrican-American:score_factorHigh` term is not statistically significant. Or, as ProPublica puts it, it's "almost statistically significant".
3. African Americans have a much higher than average recidivism rate - see the `race_factorAfrican-American` term.

Looks like a big win for machine learning, right? The statistical algorithm predicts criminal recidivism and it does in a way that any racial bias present cannot be distinguished from random chance.

Somehow, Julie Angwin at ProPublica managed to title her article [Machine Bias: There’s software used across the country to predict future criminals. And it’s biased against blacks.](https://www.propublica.org/article/machine-bias-risk-assessments-in-criminal-sentencing) Furthermore, most casual readers of the article seem to think it's making a solid case.

What the fuck? Am I the only person who looks at numbers? Apparently so.

### How they did it

One big tool in lying without statistics is to tell a story or two. Include vivid but irrelevant detail - humans immediately latch onto that stuff, statistically irrelevant though it may be:

> ON A SPRING AFTERNOON IN 2014, Brisha Borden was running late to pick up her god-sister from school when she spotted an unlocked kid’s blue Huffy bicycle and a silver Razor scooter. Borden and a friend grabbed the bike and scooter...
> ...3 paragraphs later...
> Compare their crime with a similar one: The previous summer, 41-year-old Vernon Prater was picked up for shoplifting $86.35 worth of tools...

The article included over 10 anecdotes, all carefully loaded to suggest that the algorithm routinely gets things wrong and in a racist manner. Thirteen photographs of humans were included in this vivid narrative.

In contrast, only 2 graphs and 1 data table were included. There was no mention made of the lack of statistical significance of their primary model.

Make no mistake - the algorithm does get things wrong. All algorithms do. No matter how good an algorithm may be, you can always find such anecdotes. You can also find anecdotes going the opposite way - if they put the effort in, they easily could have dug up a black gangster who kills prostitutes with a high risk score, and who did in fact re-offend. Anecodtes prove nothing - that's why we do statistics.

The next tool is to include lots of interesting, but irrelevant, descriptive statistics:

> We ran a statistical test that isolated the effect of race from criminal history and recidivism, as well as from defendants’ age and gender. Black defendants were still 77 percent more likely to be pegged as at higher risk of committing a future violent crime and 45 percent more likely to be predicted to commit a future crime of any kind.

Random percentages sure make us look data driven, right? This fact is curious, but doesn't prove their case at all. This fact could easily be caused simply by an algorithm *accurately* predicting a higher rate of recidivism among blacks. If we scroll up, we see the data *had this exact effect*.

The article also highlights tiny differences:

> Their study also found that the score was slightly less predictive for black men than white men — 67 percent versus 69 percent.

The study referenced is [this validation study](http://www.northpointeinc.com/files/publications/Criminal-Justice-Behavior-COMPAS.pdf). So what's the driver of this difference? Simple multiplication of the numbers in table 7 shows that it's 2% x 296 black criminals in the sample = 6 people. I didn't run a statistical test, but I seriously doubt that's statistically significant.

Finally, the article includes a table of false positive probabilities (FPP) and false negative probabilities (FNP). This may or may not be evidence of bias - the authors would need to run a statistical test to determine that, which they don't. In fact, I can't even find the place in their R notebook where they did that calculation. Is this the result of bad statistics? Is it merely random chance? Who knows!

## Why I'm criticizing this article

Bias in the criminal justice system is prevalent. Humans are known to be intrinsically racist, and often irrationally so - is it any surprise that a justice system made of up humans would also be racist?

In contrast, the Cox model has no intrinsic prediliction for racism. In addition, according to multiple independent statistical analyses, any racial bias in the Cox model cannot be distinguished from random chance. Does anyone believe that bias in the human justice system is so small that we can't measure it?

So in short, we've taken a flawed and racist human system and replaced it with a much better machine learning system. We've reduced the racism in the world. This is great!

Yet in order to sell clickbait, ProPublica has decided to spread dishonest mood affiliation (with no statistics!) criticizing the much better system. Consider the possibility; ProPublica's anecdotal criticism of the Cox model finds legs, and politicians decide to replace the automated system with a human one. If we do this, **racism will increase!** That's probably not what most of the right-thinking anti-racist people outraged by this story expect, yet that's the inevitable result.

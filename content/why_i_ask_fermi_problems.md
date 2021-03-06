title: Why I ask 'how many golf balls fit on a bus?' on job interviews
date: 2012-05-12 10:00
author: Chris Stucchio
tags: hiring




In a recent hacker news [thread](http://news.ycombinator.com/item?id=3958347), a great deal of criticism was heaped on [Fermi problems](https://en.wikipedia.org/wiki/Fermi_problem). "How many golf balls fit on a double decker bus?" "How many piano tuners live in Seattle?" I think much of the criticism is unfounded, since Fermi problems come up all the time in computing.


Here is another Fermi problem:

> How many fashion items are available for sale on the internet at any given time?

The answer I cooked up was 5-10 million. But why does this matter? At the time, I was CTO of [Styloot](http://styloot.com) and I was building a particular sort of [search engine](http://styloot.com/s/parametric_search/choose_category.html). We had originally built it in Django and Postgres (using pretty ordinary SQL queries), but the performance was simply disastrous. So I was evaluating other approaches.

One approach was some sort of distributed service which would store indices and the client would piece the answer together. Another approach was a single server index, backed by the disk. A third option was a single server index, but stored entirely in memory.

Here is a second problem with a more precise answer:

> How many fashion items can be indexed in RAM on an AWS m2.2xlarge instance (34GB ram)?

The answer is about 35 million. In-memory it is! Now I know I should build [Hobo](https://github.com/stucchio/Hobo) rather than set up some Solr instance.

Another Fermi problem I saw recently:

> How many users could conceviably view a single local newspaper's website concurrently? The local newspaper should be considered to be for a small region - Hoboken or Forest Hills, not New York City.

The context was in building a realtime monitoring system. Again, this informs a design decision - is sharding based on locality a reasonable strategy to build a scalable realtime monitoring system? In the worst case, can a single server handle all the monitoring for a given locality?

The goal is not to get a precise answer. The goal is to figure out the relative orders of magnitude and then compare it to a hard number.

I often do ask at least one of these questions on an interview. I don't do it because I care about a precise answer or whether you know the exact dimensions of a golf ball. I care simply because if you can't do Fermi calculations, you can't make long term architectural decisions. You'll build a system which handles 2x today's load very nicely and which I need to replace in 2-3 years, or you might overarchitect a system which can handle 1000x more load than I'll ever need.

Orders of magnitude matter, even in the absence of precise estimates.

P.S. An edit, in response to comments: My Fermi questions are usually closer to "how many fashion items" than "how many golf balls", and are usually embedded in a bigger problem (either architectural or algorithmic). But the underlying skillset is the same.

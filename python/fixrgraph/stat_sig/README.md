# Statistical significance module

## Overview of statistical testing
This module implements the tools to perform *statistical hypothesis
testing* for the mined patterns.

We test if the patterns that we mine could have been obtained mining a
random set of data: if that is the case, then our results are not
statistically significant. Thus, our goal is to reject the *null
hypothesis* that the patterns could have been obtained from a random
set of data.

If we do not reject the null hypothesis, then our mining algorithm
effectively mines random colocation of methods, and hence it's results
are not useful. If we reject the null hypothesis, then we show
that the results is not obtained casually. We do not show that our
results are "correct", since other hypothesis are still possible.


We perform statistical hypothesis testing as follows:

- We define a *null model*. The null model is a generative model
  defining how we can get a pattern "randomly". It represents our null
  hypothesis.

- We set a significance level alpha (e.g., 0.05), the
  probability of rejecting the null hypothesis assuming that it is
  true.

- We compute the probability of obtaining such pattern in the null
  model (*p-value*?).

- If the probability of obtaining the pattern under the null model is
  below alpha, then we reject the null hypothesis.


## Binomial Null Model
In the context of API usage patterns, and complex objects such as
ACDFG (groums), we could define different null models.

Our requirements are:

- we want a model that makes the computation of the p-value simple enough
  pattern. An arbitrary complex model may require the compute complex
  conditional distributions, or select different parameters.
  
- the model should describe the most important features of the graph,
  such as the control flow.


We consider as null model a set of random variables, each one
representing the presence of a "feature" in the graph. We pick as
features the existence of an edge from a method node "m1" to a method
node "m2". Such features represent some aspect of a groum, and in
particular an abstraction of the control flow. We further assume these
variables the be independent (they are not, but...). We do *not*
consider other features, for example the one regarding the data flow
in the groum. In fact, it became very unrealistic that such features,
and the control-flow one, are independent (for example, consider the
"production and consumption" of types).


The model is defined as follows:
- `{f1, ..., fn}` is the set of features that we found in the dataset.

- Given a pattern `G`, the probability that the null model produce G is:
 
  ```P_H(G) = P(f1 | C) * ... * P(fn | C)```

  where `C = {c | c is a method call in G}`


- We get `P(f | C)` from the data: it is the number of times the
  features `f` appeared in a groum in the dataset that also contained
  all the method calls in the set `C`.

The tools performs two tasks:

1. Given a dataset of groums, extracts the features and saves them in
   a database (or particular index?)
   
2. Given a groum 'G' (a pattern), computes the probability 'P_H(G)' to
   obtain 'G' from the null model.


## Dependencies

The module inserts and queries the data from a MySQL database. You have to set-up a MySQL server.

```
sudo apt-get install mysql-server libmysqlclient-dev
```

The module uses the mysql client:

```
pip install mysqlclient
```


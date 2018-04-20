---
layout: main
---
# BigGroum {#biggroum}

BigGroum is a programming pattern-mining tool for finding patterns conserved across corpora consisting of hundreds or even thousands of projects.

Frameworks like Android expose rich functionality through a complex, object-oriented application-programming interface (API). How to properly use API methods is rarely fully documented and so app developers may guess incorrectly. BigGroum reifies in a mining tool the intuitive approach of looking for examples of how others use the API. The underlying assumption is that a “popular” way of using the API probably works, and code that is slightly off from a popular pattern is suspicious. To accurately capture API usage patterns, BigGroum mines graph-based object usage models (groums) that simultaneously describe control flow and data dependencies between methods of multiple interacting object types.

The repository for the BigGroum tool can be found [here](http://github.com/cuplv/biggroum)


## References and experiments {#references-and-experiments}

The techniques implemented by the tool are described in the paper:
```
Mining Framework Usage Graphs from App Corpora,
Sergio Mover, Sriram Sankaranarayanan, Rhys Braginton Pettee Olsen, Bor-Yuh Evan Chang,
IEEE International Conference on Software Analysis, Evolution and Reengineering, 2018
```

A copy of a pre-print of the paper is available in the doc folder.

In the paper we used the `BigGroum` tool to extract and mine patterns from 500 Android applications. The results are available [here](https://goo.gl/r1VAgc)



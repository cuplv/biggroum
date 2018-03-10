---
layout: main
---
# BigGroum {#biggroum}

We write modern software, as Android application, using existing, external libraries that provide a rich set of functionalities through an Application Programming Interface (API). The use of API methods is often not fully documented and developers often do not know how to use the API methods or use the API incorrectly.
The BigGroum tool mines a graph (Groum) representation of the popular API usage, a pattern, from a large code base of existing software projects. The mined patterns can be either used to document how a set of API is used and to automatically detect likely incorrect usages of the APIs.


The repository for the BigGroum tool can be found [here](http://github.com/cuplv/biggroum/settings)


## References and experiments {#references-and-experiments}

The techniques implemented by the tool are described in the paper:
```
Mining Framework Usage Graphs from App Corpora,
Sergio Mover, Sriram Sankaranarayanan, Rhys Braginton Pettee Olsen, Bor-Yuh Evan Chang,
IEEE International Conference on Software Analysis, Evolution and Reengineering, 2018
```

A copy of a pre-print of the paper is available in the doc folder.

In the paper we used the `BigGroum` tool to extract and mine patterns from 500 Android applications. The results are available [here](https://goo.gl/r1VAgc)



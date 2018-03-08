# FixrGraph

We write modern software, as Android application, using existing, external libraries that provide a rich set of functionalities through an Application Programming Interface (API). The use of API methods is often not fully documented and developers often do not know how to use the API methods or use the API incorrectly.     
The BigGroum tool mines a graph representation of the popular API usage, a pattern, from a large code base of existing software projects. The mined patterns can be either used to document how a set of API is used and to automatically detect likely incorrect usages of the APIs.


This repository contains the code that calls the extraction of the graphs (GROUMS) from an Android App and then performs the mining task.


# Subprojects

The extraction of the graphs and the implementation of the mining
algorithm is implemented in the FixrGraphExtractor and FixrGraphIso
submodules.




# Installation and dependencies

1. Follow the README files in the `FixrGraphExtractor` and
   `FixrGraphIso` to check the required dependencies of both tools.


To build the `FixrGraphExtractor`:
```
$> cd FixrGraphExtractor
$> sbt oneJar
```

To build `FixrGraphIso`:
```
$> cd FixrGraphIso
$> mkdir build
$> cd build
$> cmake ../ -DFIXR_GRAPH_EXTRACTOR_DIRECTORY=../../FixrGraphExtractor
$> make
```


2. Install the following dependencies to use the automated scripts to run the graph extraction and graph mining computation:
- python 2.7
- enum34 python package (`pip install enum34`)
- protobuf (`pip install protobuf`)
- sql_alchemy for python


- android SDK
Remember to set the android SDK home

3. To test if your environment is set-up correctly, you can run the tests.
```
$> cd python/fixrgraph/test
$> nosetests
```

You need to have `nose` installed on your system to run the tests automatically. It can be installed using `pip` via `pip install nose`




# Run the graph extraction and mining process

You need to include the python package in your `PYTHON_PATH`.
You can execute the following command from the repository path:
```
repo_path=`pwd`
export PYTHONPATH="${repo_path}/python":${PYTHONPATH}
```



## Set-up the extraction step:

The file `scripts/sample_setup/config.txt` shows an example of parameters that can be used to setup the extraction and mining process.

Note that the file paths in the configiration file must be absolute or relative to the path where the script is executed.

### repo_list
Path to a json file containing the name of the github repository that must be processed (see the file `scripts/sample_setup/repo_list.json`)

### buildable_list
Path to a json file describing where the github repositories have been already built.

See the file `buildable_small.json` file to see the information that must be provided.

### build_data
Path to the directory that contains the built repositories.

Each repository must be built in a folder called `<github-username>/<github-repo-name>/<github-commit-hash>`.

### out_path
Output directory for all the produced data (you have to create the folder `out` under `scripts/sample_setup` it to run the tool on the example setup).

### frequency_cutoff
The minimum frequency of an itemset (i.e., number of graphs that support that itemset) that will be considered by the itemset computation.

### min_methods_in_itemset
The minimum number of methods that an itemset must have

[pattern]
### timeout
The timeout (in seconds) for the computation of the patterns of a single cluster

### frequency_cutoff
The minimum frequency (number of graphs) that a pattern must have to be considered frequent.


## Run the whole process
```
$> cd scripts/sample_setup
$> python run_mining.py -c config.txt
```


## Description of the output



# References and experiments

The techniques implemented by the tool are described in the paper:
```
Mining Framework Usage Graphs from App Corpora,
Sergio Mover, Sriram Sankaranarayanan, Rhys Braginton Pettee Olsen, Bor-Yuh Evan Chang,
IEEE International Conference on Software Analysis, Evolution and Reengineering, 2018
```

A copy of a pre-print of the paper is available in the doc folder.

In the paper we used the `FixrGraph` tool to extract and mine patterns from 500 Android applications. The results are available here: https://goo.gl/r1VAgc



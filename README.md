# FixrGraph
Top-level project for the graph extraction

# Subprojects
- https://github.com/cuplv/FixrGraphExtractor
- https://github.com/cuplv/FixrGraphIndexer
- https://github.com/cuplv/FixrGraphIso
- https://github.com/cuplv/FixrCommunityDetection

# Depedencies
- python 2.7
- enum34 python package (`pip install enum34`)
- protobuf (`pip install protobuf`)
- sql_alchemy for python
- android sdk (it is needed to compile the repositories)

# Steps in the graph pipeline

The graph pipeline consists of the following steps:

1. Extract the graphs

2. Filter the set of isomorphism to compute, through the creation of an index

3. Compute the isomorphism

4. Analyze the community formed by the isomorphisms

5. Find bugs for an Android application

*WARNING:* this last step is just a mockup of the program that finds bugs in the API usage


## Automatic extraction
The script `script/full_extraction.bash` automate the full pipeline
from the extraction of the graphs to the computation of the
isomorphisms.

### Download and build the necessary software

- FixrGraph project
```
$> git clone https://github.com/cuplv/FixrGraph
```

*WARNING* you must add the path to `FixrGraph/python` to the `PYTHONPATH` environment variable.


- Graph extractor
```
$> git clone https://github.com/cuplv/FixrGraphExtractor
$> cd FixrGraphExtraction
$> sbt oneJar
```

Graph isomorphism computation
```
$> sudo apt-get install libprotobuf-dev libglpk-dev protobuf-compiler
$> git clone https://github.com/cuplv/FixrGraphIso
$> mkdir graph_build
$> cd graph_build
$> cmake -DFIXR_GRAPH_EXTRACTOR_DIRECTORY=<PATH TO FixrGraphExtractor> ..
$> make
```

- Isomorphism computation indexer and scheduler
```
$> cd FixrGraphIndexer
$> sbt oneJar
```

- FixrCommunityDetection
```
$> cd FixrCommunityDetection
$> sbt assembly
```


### Run the full pipeline

Set up the local configuration:
```
$> cp scripts/config_template.bash script/config.bash
```

Edit the file `script/config.bash` setting the following parameters:
- `FIXR_GRAPH_EXTRACTOR`: path to the FixrGraphExtractor repository
- `FIXR_GRAPH_INDEXER`: path to the FixrGraphIndexer repository
- `FIXR_GRAPH_ISO_BIN`: path to the FixrGraphIso *binary*
- `FIXR_COMMUNITY_DETECTION`: path to the FixrCommunityDetection repository
- `OUT_DIR`: path to the output directory of the extraction
- `REPO_LIST`: path to the json file containing the list of repositories 
See the file `extraction_scripts/python/fixrgraph/extraction/examples/smaller.json` in the
FixrGraphExtractor repository for an example.
- `MIN_METHODS`: minimum number of methods required in a graphs to be considered for an isomorphism
- `MIN_NODES`: minimum number of nodes required in a graphs to be considered for an isomorphism
- `MIN_EDGES`: minimum number of edges required in a graphs to be considered for an isomorphism
- `MIN_COMMON_METHODS`: minimum number of common methods calls of two graphs required to be considered for an isomorphism
- `TIMEOUT`: timeout (in seconds) for the isomorphism computation
- `JOB_SIZE`: number of isomorphism computed by a single job.
- `SPARK_SUBMIT_PATH`: path to the spark command `spark-submit` (e.g. when downloading and extracting the spark tar.gz, spark-submit is found here `spark-2.0.0-bin-hadoop2.7/bin/spark-submit`)

Run the script:
```bash full_extraction.bash ./script/config.bash```

## Extraction pipeline - details and manual extraction

In the following we describe in details all the steps require to
perform the extraction and isomorphism computation.

### 1. Extract the graphs

#### 1.1. Perform the extraction
- Download and build the repo:

```
$> git clone https://github.com/cuplv/FixrGraphExtractor
$> cd FixrGraphExtraction
$> sbt oneJar
```

- Run the extraction:
```
bash ./python/fixrgraph/extraction/run_script.bash /tmp ./python/fixrgraph/extraction/examples/smaller.json
```

In this case the list of repositories to process is specified in the file `./python/fixrgraph/extraction/examples/smaller.json`.

The graphs will be extracted in the folder `/tmp` (`/tmp/src_repo`,
`/tmp/graphs`, `/tmp/provenance` for the repo, the graphs and the
provenance information respectively)

#### 1.2 Populate the db
- Download the repo:
```
$> git clone https://github.com/cuplv/FixrGraphIndexer
```

- Fill a database with the graphs
```
python ./python/fixrgraph/scheduler/process_graphs.py -g /tmp/graphs -d /tmp/graphs_db.db
```


### 2. Get the set of isomorphism to compute
- Download and build the repo:
```
$> git clone https://github.com/cuplv/FixrGraphIndexer
$> cd FixrGraphIndexer
$> sbt oneJar
```

- Create the set of isomorphisms to compute:
```
$> java -jar target/scala-2.11/fixrgraphindexer_2.11-0.1-SNAPSHOT-one-jar.jar -d /tmp/graphs -o /tmp/iso_index.json -m 2 -n 2 -e 2 -i 2
```

The command creates the index file in `/tmp/iso_index.json`


### 3. Compute the isomorphism

#### 3.1. Build the isomorphism checker
- Build the repo
```
$> git clone https://github.com/cuplv/FixrGraphIso
$> mkdir graph_build
$> cd graph_build
$> cmake -DFIXR_GRAPH_EXTRACTOR_DIRECTORY=<PATH TO FixrGraphExtractor> ../FixrGraphIso
$> make
```

The graph isomorphism executable is in `./graph_build/src/fixrgraphiso/fixrgraphiso`

#### 3.2 Creates the jobs (local or in Janus)

- Generate the scheduler jobs
```
$> cd FixrGraphIndexer
$> python ./python/fixrgraph/scheduler/create_jobs.py  -i /tmp/iso_index.json  -g /tmp/graphs -j /tmp/out_jobs -o /tmp/iso -s 2000 -b <path_to_the_isomorphism_executable> -p scheduler/run_iso.py -l /tmp -t 5
```

The parameters are:
- `-i /tmp/iso_index.json`: index for the isomorphisms
- `-g /tmp/graphs`: graphs
- `-j /tmp/out_jobs`: output folder for the jobs to be executed
- `-o /tmp/iso`: output folder for the isomorphisms to be computed
- `-s 2000`: number of isomorphisms for each job
- `-b <path_to_the_isomorphism_executable>`
- `-p scheduler/run_iso.py`: script used to execute the isomorphism
- `-t 5`: timeout for each single isomorphism

#### 3.3 Run the jobs
```
$> cd /tmp/out_jobs
$> make -f scheduler_iso_index
```

The scheduler uses make to parallelize the computation of the isomorphisms.
The isomorphisms are in `/tmp/iso`, the execcution logs of the jobs are in `/tmp/out_jobs`

#### 3.4 Collect the isomorphism in the database
```
$> cd FixrGraphIndexer
$> python ./python/fixrgraph/scheduler/process_logs.py  -s /tmp/out_jobs/scheduler_iso_index.make -j /tmp/out_jobs -n /tmp/out_jobs -g /tmp/graphs -g /tmp/graphs -o /tmp/graphs_db.db
```

*WARNING*: the insertion in the db is not idempotent (i.e. run it once!)


#### 3.4 Generate the html pages
```
$> cd FixrGraphIndexer
$> python ./python/fixrgraph/provenance/gen_html.py  -d /tmp/graphs_db.db -o /tmp/index -g /tmp/graphs -p /tmp/provenance -i /tmp/iso
```

### 4. Analyze the community formed by the isomorphisms
```
$> cd FixrCommunityDetection
$> 
```


### 5. Find bugs 

```
python ./python/fixrgraph/bugfinding/find_bugs.py -r Appdynamics:ECommerce-Android:47d3ad75ef25da3e3cc7c9b6dc7d9f490e8ebac6 -i /tmp/myout/src_repo -o /tmp/cavallo -j /home/sergio/works/projects/muse/repos/FixrGraphExtractor/target/scala-2.11/fixrgraphextractor_2.11-0.1-SNAPSHOT-one-jar.jar 
```


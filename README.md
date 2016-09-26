# FixrGraph
Top-level project for the graph extraction

# Subprojects
- https://github.com/cuplv/FixrGraphExtractor
- https://github.com/cuplv/FixrGraphIndexer
- https://github.com/cuplv/FixrGraphIso
- https://github.com/cuplv/FixrCommunityDetection


# Steps in the graph pipeline

The graph pipeline consists of the following steps:
1. Extract the graphs
2. Filter the set of isomorphism to compute, through the creation of an index
3. Compute the isomorphism
4. Analyze the community formed by the isomorphisms


## 1. Extract the graphs

### 1.1. Perform the extraction
- Download and build the repo:

```$> git clone https://github.com/cuplv/FixrGraphExtractor
$> cd FixrGraphExtraction
$> sbt oneJar```

- Run the extraction:
```bash ./extraction_scripts/run_script.bash /tmp ./extraction_scripts/examples/smaller.json```

In this case the list of repositories to process is specified in the file `./extraction_scripts/examples/smaller.json`.

The graphs will be extracted in the folder `/tmp` (`/tmp/src_repo`,
`/tmp/graphs`, `/tmp/provenance` for the repo, the graphs and the
provenance information respectively)

### 1.2 Populate the db
- Download the repo:
```$> git clone https://github.com/cuplv/FixrGraphIndexer```

- Fill a database with the graphs
```python scheduler/process_graphs.py -g /tmp/graphs -d /tmp/graphs_db.db```


## 2. Get the set of isomorphism to compute
- Download and build the repo:
```$> git clone https://github.com/cuplv/FixrGraphIndexer
$> cd FixrGraphIndexer
$> sbt oneJar```

- Create the set of isomorphisms to compute:
```$> java -jar target/scala-2.11/fixrgraphindexer_2.11-0.1-SNAPSHOT-one-jar.jar -d /tmp/graphs -o /tmp/iso_index.json -m 2 -n 2 -e 2 -i 2```

The command creates the index file in `/tmp/iso_index.json`


## 3. Compute the isomorphism

### 3.1. Build the isomorphism checker
- Download the repo:
```$> git clone https://github.com/cuplv/FixrGraphIso```

- Build the repo
```
$> mkdir graph_build
$> cd graph_build
$> cmake ../FixrGraphIso
$> make
```

The graph isomorphism executable is in `./graph_build/src/fixrgraphiso/fixrgraphiso`

### 3.2 Creates the jobs (local or in Janus)

- Generate the scheduler jobs
```$> cd FixrGraphIndexer
$> python scheduler/create_jobs.py  -i /tmp/iso_index.json  -g /tmp/graphs -j /tmp/out_jobs -o /tmp/iso -s 2000 -b <path_to_the_isomorphism_executable> -p scheduler/run_iso.py -t 5```

The parameters are:
- `-i /tmp/iso_index.json`: index for the isomorphisms
- `-g /tmp/graphs`: graphs
- `-j /tmp/out_jobs`: output folder for the jobs to be executed
- `-o /tmp/iso`: output folder for the isomorphisms to be computed
- `-s 2000`: number of isomorphisms for each job
- `-b <path_to_the_isomorphism_executable>`
- `-p scheduler/run_iso.py`: script used to execute the isomorphism
- `-t 5`: timeout for each single isomorphism

### 3.3 Run the jobs
```$> cd /tmp/out_jobs
$> make -f scheduler_iso_index```

The scheduler uses make to parallelize the computation of the isomorphisms.
The isomorphisms are in `/tmp/iso`, the execcution logs of the jobs are in `/tmp/out_jobs`

### 3.4 Collect the isomorphism in the database
```$> cd FixrGraphIndexer
$> python scheduler/process_logs.py  -s /tmp/out_jobs/scheduler_iso_index.make -j /tmp/out_jobs -n /tmp/out_jobs -g /tmp/graphs -g /tmp/graphs -o /tmp/graphs_db.db```

*WARNING*: the insertion in the db is not idempotent (i.e. run it once!)

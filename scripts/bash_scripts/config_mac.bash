#!/bin/bash

EXTRACTOR_STATUS_FILE=extractor_status

FIXR_GRAPH_EXTRACTOR=/Users/sergiomover/works/projects/muse/repos/FixrGraphExtractor
FIXR_GRAPH_INDEXER=/Users/sergiomover/works/projects/muse/repos/FixrGraphIndexer
FIXR_GRAPH_ISO=/Users/sergiomover/works/projects/muse/repos/FixrGraphIso
FIXR_GRAPH_ISO_BIN=/Users/sergiomover/works/projects/muse/repos/FixrGraphIso/build/src/fixrgraphiso/fixrgraphiso
FIXR_COMMUNITY_DETECTION=/Users/sergiomover/works/projects/muse/repos/FixrCommunityDetection

BUILDABLE_REPOS_LIST=/Users/sergiomover/works/projects/muse/repos/buildable.json
BUILDABLE_REPOS_PATH=/Users/sergiomover
REPO_LIST=/Users/sergiomover/works/projects/muse/repos/FixrGraph/scripts/app.json

OUT_DIR=/Users/sergiomover/works/projects/muse/test_extraction
SPARK_SUBMIT_PATH=/home/sergio/Tools/spark-2.0.0-bin-hadoop2.7/bin/spark-submit

# Index options
# Index options
MIN_METHODS=2
MIN_NODES=2
MIN_EDGES=3
MIN_COMMON_METHODS=2

# options for clustering
FREQ_CUTOFF=3
MIN_METH=2


# ISO OPTIONS
TIMEOUT=5
JOB_SIZE=1000

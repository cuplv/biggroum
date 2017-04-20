#!/bin/bash

EXTRACTOR_STATUS_FILE=cavallo

FIXR_GRAPH_EXTRACTOR=/home/ubuntu/FixrGraphExtractor
FIXR_GRAPH_INDEXER=/home/ubuntu/FixrGraphIndexer
FIXR_GRAPH_ISO=/home/ubuntu/FixrGraphIso
FIXR_GRAPH_ISO_BIN=/home/ubuntu/FixrGraphIso/build/src/fixrgraphiso/fixrgraphiso
FIXR_COMMUNITY_DETECTION=/home/ubuntu/FixrCommunityDetection

BUILDABLE_REPOS_LIST=/home/ubuntu/buildable.json
BUILDABLE_REPOS_PATH=/build-data/staging1
REPO_LIST=/home/ubuntu/FixrGraph/python/fixrgraph/extraction/examples/smaller.json

OUT_DIR=/tmp/testextraction
SPARK_SUBMIT_PATH=/home/sergio/Tools/spark-2.0.0-bin-hadoop2.7/bin/spark-submit

# Index options
# Index options
MIN_METHODS=2
MIN_NODES=2
MIN_EDGES=3
MIN_COMMON_METHODS=2

# options for clustering
FREQ_CUTOFF=3
MIN_METH=3


# ISO OPTIONS
TIMEOUT=5
JOB_SIZE=1000

#!/bin/bash

FIXR_GRAPH_EXTRACTOR=/home/sergio/works/projects/muse/repos/FixrGraphExtractor
FIXR_GRAPH_INDEXER=/home/sergio/works/projects/muse/repos/FixrGraphIndexer
FIXR_GRAPH_ISO=/home/sergio/works/projects/muse/repos/FixrGraphIso
FIXR_GRAPH_ISO_BIN=/home/sergio/works/projects/muse/repos/FixrGraphIso/build/src/fixrgraphiso/fixrgraphiso
FIXR_COMMUNITY_DETECTION=/home/sergio/works/projects/muse/repos/FixrCommunityDetection

BUILDABLE_REPOS_LIST=/home/sergio/works/projects/muse/repos/FixrRelevantCodeSearch/scripts/buildable.json
BUILDABLE_REPOS_PATH=/home/sergio/works/projects/muse/buildable
REPO_LIST=/home/sergio/works/projects/muse/repos/FixrGraph/python/fixrgraph/extraction/examples/smaller.json

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

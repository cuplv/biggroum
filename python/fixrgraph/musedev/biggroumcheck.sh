#!/bin/bash

# Use:  In the .muse.toml specify:
# ```
# customTools = "https://raw.githubusercontent.com/cuplv/biggroum/master/python/fixrgraph/musedev/biggroumcheck.sh"
# ```
#
# to invoke the script: ./biggroumcheck.sh <filepath> <commit> <command>
# For example:
# echo '{ "residue" : {}, "cwd" : "", "cmd" : "", "args" : "", "classpath" : [],  "files" : ["file1.java", "file2.java"]}' | ./biggroumcheck.sh 1 2 run
#
dir=$1
commit=$2
cmd=$3
shift
shift
shift
echo "dir: ${dir}" 1>&2
echo "commit: ${commit}" 1>&2
echo "cmd: ${cmd}" 1>&2


# perform initalization tasks
# - download the biggroum repository with the fixrgraph python package
# - download the graph extractor
# - download the biggroum
# - set the PYTHONPATH and GRAPH_EXTRACTOR_PATH
# Redirects all the output to the setup_log file
if [[ -z "${ENV_SETUP}" ]]; then
    # Getting back here when the setup is done --- do everything in the home
    pushd . >> pre_setup_log 2>&1 && \
        mkdir ${HOME}/biggroumsetup >> pre_setup_log 2>&1 && \
        cd ${HOME}/biggroumsetup >>setup_log 2>&1 && \
        apt install -y wget python-pip >>setup_log 2>&1 && \
        pip install --quiet nose requests >>setup_log 2>&1 && \
        wget https://github.com/cuplv/FixrGraphExtractor/releases/download/v1.0-musedev/fixrgraphextractor_2.12-0.1.0-one-jar.jar >>setup_log 2>&1 && \
        export GRAPH_EXTRACTOR_PATH="${PWD}/fixrgraphextractor_2.12-0.1.0-one-jar.jar" >>setup_log 2>&1 && \
        git clone https://github.com/cuplv/biggroum.git >>setup_log 2>&1 && \
        cd biggroum >>setup_log 2>&1 && \
        git checkout musedev_hackaton >>setup_log 2>&1 && \
        git pull >>setup_log 2>&1 && \
        export PYTHONPATH="${HOME}/biggroumsetup/biggroum/python:$PYTHONPATH"  >>setup_log 2>&1 && \
        export ENV_SETUP="1" >>setup_log 2>&1

    # TODO: Fix, not robust if initial pushd fails
    popd >>setup_log 2>&1
fi

if [[ -z "${GRAPH_EXTRACTOR_PATH}" ]]; then
    echo "GRAPH_EXTRACTOR_PATH not set. Exit with an error." 1>&2
    exit 1 1>&2
else
    graph_extractor_path="${GRAPH_EXTRACTOR_PATH}"  1>&2
fi

if [[ -z "${FIXR_SEARCH_ENDPOINT}" ]]; then
    # DEFAULT ADDRESS FOR THE SERVER --- TO SET UP WHEN WE DEPLOY IT!
    FIXR_SEARCH_ENDPOINT="http://localhost:8081/process_muse_data" 1>&2
else
    fixr_search_endpoint="${FIXR_SEARCH_ENDPOINT}" 1>&2
fi

# Call the script invoking biggroum
cd "$(dirname "${BASH_SOURCE[0]}")"
python biggroumscript.py "${dir}" "${commit}" "${cmd}" "${graph_extractor_path}" "${fixr_search_endpoint}" < /dev/stdin 1> /dev/stdout 2> /dev/stderr
exit $?

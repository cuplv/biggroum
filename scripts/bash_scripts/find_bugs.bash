#!/bin/bash

check_empty() {
    local param=$1
    local msg=$2

    if [ "${param}X" == "X" ]; then
        echo "${msg} not provided!"
        exit 1
    fi
}

check_exists(){
    local file=$1
    local msg=$2

    if [ ! -f "${file}" ] && [ ! -d "${file}" ] ; then
        echo "${msg}: ${file} does not exists!"
        exit 1
    fi
}


check_res() {
    local res=$1
    local msg=$2

    if [ "${res}X" != "0X" ]; then
        echo "Error code ${res}: ${msg}"
        exit 1
    fi
}


rl="$(readlink -f "$0")"
script_dir="$(dirname "${rl}")"

config_script=$1
user_name=$2
repo_name=$3
commit_hash=$4
base_dir=$5

check_empty "${user_name}" "User name does not provided"
check_empty "${repo_name}" "Repo name does not provided"
check_empty "${commit_hash}" "Commit hash does not provided"
check_empty "${base_dir}" "App base directory not provided"

#config_script="${script_dir}/config.bash"

check_exists "${config_script}" "config.bash script was not provided!"

source ${config_script}

FIXR_GRAPH_PYTHON="$(readlink -f "${script_dir}/../python/fixrgraph/")"
FIXR_GRAPH_EXTRACTOR_JAR="$(readlink -f ${FIXR_GRAPH_EXTRACTOR}/target/scala-2.11/fixrgraphextractor_2.11-0.1-SNAPSHOT-one-jar.jar)"

check_exists "${FIXR_GRAPH_EXTRACTOR}" "FixrGraphExtractor folder"
check_exists "${FIXR_GRAPH_EXTRACTOR_JAR}" "FixrGraphExtractor jar does not exist: did you run sbt oneJar there?"
check_exists "${FIXR_GRAPH_PYTHON}" "Python package"

if [ ! -d "${OUT_DIR}" ] ; then
    echo "${OUT_DIR} does not exist!"
    exit 1
fi

python ${FIXR_GRAPH_PYTHON}/bugfinding/find_bugs.py -r "${user_name}:${repo_name}:${commit_hash}" -i ${base_dir} -o ${OUT_DIR} -j ${FIXR_GRAPH_EXTRACTOR_JAR} 


#!/bin/bash

usage() {
    echo "$0 <outputpath> <repolist>"
    exit 1
}

is_empty() {
    local path="$1"
    local descr="$2"

    if [ "${path}" == "" ]; then
        echo "${descr} is empty!"
        usage
    fi
}

dir_exists() {
    local path="$1"
    local descr="$2"

    if [ ! -d "${path}" ]; then
        echo "${descr} (${path}) does not exists!"
        usage
    fi
}

file_exists() {
    local path="$1"
    local descr="$2"

    if [ ! -f "${path}" ]; then
        echo "${descr} (${path}) does not exists!"
        usage
    fi
}

OUT_BASE="${1}"
REPO_LIST="${2}"

is_empty "${OUT_BASE}" "Output path"
dir_exists "${OUT_BASE}" "Output path"
is_empty "${REPO_LIST}" "List of repos"
file_exists "${REPO_LIST}" "List of repos"

is_empty "${ANDROID_HOME}" "Android home"
dir_exists "${ANDROID_HOME}" "Android home"

current_dir=`dirname $0`
SCRIPTPATH=`cd ${current_dir} && pwd -P`

EXTRACTOR_SCRIPT=${SCRIPTPATH}/run_extractor.py
file_exists "${EXTRACTOR_SCRIPT}" "Extractor script"
EXTRACTOR_JAR=${SCRIPTPATH}/../target/scala-2.11/fixrgraphextractor_2.11-0.1-SNAPSHOT-one-jar.jar
file_exists "${EXTRACTOR_JAR}" "Extractor jar"

REPO_PATH=${OUT_BASE}/src_repo
GRAPHS_PATH=${OUT_BASE}/graphs
PROVENANCE_PATH=${OUT_BASE}/provenance
mkdir -p ${REPO_PATH}
mkdir -p ${GRAPHS_PATH}
mkdir -p ${PROVENANCE_PATH}

python ${EXTRACTOR_SCRIPT} -a ${REPO_LIST} -i ${REPO_PATH} -g ${GRAPHS_PATH} -p ${PROVENANCE_PATH} -f android -j ${EXTRACTOR_JAR}

exit $?

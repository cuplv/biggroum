#!/bin/bash

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

#config_script="${script_dir}/config.bash"

check_exists "${config_script}" "config.bash script was not provided!"

source ${config_script}

FIXR_GRAPH_EXTRACTOR_JAR="$(readlink -f ${FIXR_GRAPH_EXTRACTOR}/target/scala-2.11/fixrgraphextractor_2.11-0.1-SNAPSHOT-one-jar.jar)"
FIXR_COMMUNITY_DETECTION_JAR="$(readlink -f ${FIXR_COMMUNITY_DETECTION}/target/scala-2.11/FixrCommunityDetection-assembly-0.1-SNAPSHOT.jar)"

check_exists "${FIXR_GRAPH_EXTRACTOR}" "FixrGraphExtractor folder"
check_exists "${FIXR_GRAPH_EXTRACTOR_JAR}" "FixrGraphExtractor jar does not exist: did you run sbt oneJar there?"
#check_exists "${FIXR_GRAPH_INDEXER}" "FixrGraphIndexer folder"
#check_exists "${FIXR_GRAPH_ISO_BIN}" "FixrGraphIso binary"
#check_exists "${FIXR_COMMUNITY_DETECTION}" "FixrCommunityDetection path"
#check_exists "${FIXR_COMMUNITY_DETECTION_JAR}" "FixrCommunityDetection jar does not exist: did you run sbt assembly there?"
check_exists "${REPO_LIST}" "List of repositories"
#check_exists "${SPARK_SUBMIT_PATH}" "Spark submit executable"

check_exists "${BUILDABLE_REPOS_LIST}" "List of buildable repos"
check_exists "${BUILDABLE_REPOS_PATH}" "Path to the built repos"

FIXR_GRAPH_PYTHON="$(readlink -f "${script_dir}/../python/fixrgraph/")"
check_exists "${FIXR_GRAPH_PYTHON}" "Python package"


if [ "${EXTRACTOR_STATUS_FILE}X" == "X" ]; then
    echo "EXTRACTOR_STATUS_FILE not set"
    exit 1
fi

if [ -d "${OUT_DIR}" ] ; then
    echo "Warning: ${OUT_DIR} already exists. Data will be duplicated"
else
    mkdir -p "${OUT_DIR}"
fi

OUT_LOG=${OUT_DIR}/out_log.txt
if [ -f "${OUT_LOG}" ]; then
    OUT_LOG_OLD=${OUT_LOG}
    OUT_LOG="${OUT_DIR}/out_log_$$.txt"
    echo "Warning: ${OUT_LOG_OLD} already exists. Log file is ${OUT_LOG}"
fi

# Extract the graphs
echo "Extracting graphs from ${REPO_LIST}..."
pushd .
cd ${OUT_DIR}
echo "bash ${FIXR_GRAPH_PYTHON}/extraction/run_script.bash ${OUT_DIR} ${REPO_LIST} ${FIXR_GRAPH_EXTRACTOR_JAR} ${BUILDABLE_REPOS_LIST} ${BUILDABLE_REPOS_PATH} ${EXTRACTOR_STATUS_FILE} &>> ${OUT_LOG}" &>> ${OUT_LOG}
bash ${FIXR_GRAPH_PYTHON}/extraction/run_script.bash ${OUT_DIR} ${REPO_LIST} ${FIXR_GRAPH_EXTRACTOR_JAR} ${BUILDABLE_REPOS_LIST} ${BUILDABLE_REPOS_PATH} ${EXTRACTOR_STATUS_FILE} &>> ${OUT_LOG}
res=$?
popd
check_res "${res}" "Extract graphs of ${REPO_LIST}"

echo "Filling graph dbs..."
echo "python ${FIXR_GRAPH_PYTHON}/db/scripts/process_graphs.py -g ${OUT_DIR}/graphs -d ${OUT_DIR}/graphs_db.db" &>> ${OUT_LOG}
python ${FIXR_GRAPH_PYTHON}/db/scripts/process_graphs.py -g ${OUT_DIR}/graphs -d ${OUT_DIR}/graphs_db.db &>> ${OUT_LOG} 
check_res "$?" "Fill graph db"
echo "Filled graph dbs..."

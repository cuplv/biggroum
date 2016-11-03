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
config_script="${script_dir}/config.bash"
check_exists "${config_script}" "config.bash does not exists"
source ${config_script}

FIXR_GRAPH_EXTRACTOR_JAR="$(readlink -f ${FIXR_GRAPH_EXTRACTOR}/target/scala-2.11/fixrgraphextractor_2.11-0.1-SNAPSHOT-one-jar.jar)"
FIXR_COMMUNITY_DETECTION_JAR="$(readlink -f ${FIXR_COMMUNITY_DETECTION}/target/scala-2.11/FixrCommunityDetection-assembly-0.1-SNAPSHOT.jar)"

check_exists "${FIXR_GRAPH_EXTRACTOR}" "FixrGraphExtractor folder"
check_exists "${FIXR_GRAPH_EXTRACTOR_JAR}" "FixrGraphExtractor jar does not exist: did you run sbt oneJar there?"
check_exists "${FIXR_GRAPH_INDEXER}" "FixrGraphIndexer folder"
check_exists "${FIXR_GRAPH_ISO_BIN}" "FixrGraphIso binary"
check_exists "${FIXR_COMMUNITY_DETECTION}" "FixrCommunityDetection path"
check_exists "${FIXR_COMMUNITY_DETECTION_JAR}" "FixrCommunityDetection jar does not exist: did you run sbt assembly there?"
check_exists "${OUT_DIR}" "Output directory"
check_exists "${REPO_LIST}" "List of repositories"
check_exists "${SPARK_SUBMIT_PATH}" "Spark submit executable"

FIXR_GRAPH_PYTHON="$(readlink -f "${script_dir}/../python/fixrgraph/")"
check_exists "${FIXR_GRAPH_PYTHON}" "Python package"



OUT_LOG=${OUT_DIR}/out_log.txt

# Extract the graphs
echo "Extracting graphs from ${REPO_LIST}..."
pushd .
cd ${OUT_DIR}
bash ${FIXR_GRAPH_PYTHON}/extraction/run_script.bash ${OUT_DIR} ${REPO_LIST} ${FIXR_GRAPH_EXTRACTOR_JAR} &>> ${OUT_LOG}
res=$?
popd
check_res "${res}" "Extract graphs of ${REPO_LIST}"

echo "Filling graph dbs..."
echo "python ${FIXR_GRAPH_PYTHON}/db/scripts/process_graphs.py -g ${OUT_DIR}/graphs -d ${OUT_DIR}/graphs_db.db &>> ${OUT_LOG}"
python ${FIXR_GRAPH_PYTHON}/db/scripts/process_graphs.py -g ${OUT_DIR}/graphs -d ${OUT_DIR}/graphs_db.db &>> ${OUT_LOG}
check_res "$?" "Fill graph db"

# Generate the index
echo "Generating the index..."
java -jar ${FIXR_GRAPH_INDEXER}/target/scala-2.11/fixrgraphindexer_2.11-0.1-SNAPSHOT-one-jar.jar -d ${OUT_DIR}/graphs -o ${OUT_DIR}/iso_index.json -m ${MIN_METHODS} -n ${MIN_NODES} -e ${MIN_EDGES} -i ${MIN_COMMON_METHODS} &>> ${OUT_LOG}
check_res "$?" "Index generation"

# Compute the isomorphism
echo "Schedule the isomorphism computation..."
python ${FIXR_GRAPH_PYTHON}/scheduler/create_jobs.py  -i ${OUT_DIR}/iso_index.json  -g ${OUT_DIR}/graphs -j ${OUT_DIR}/out_jobs -o ${OUT_DIR}/iso -s ${JOB_SIZE} -b ${FIXR_GRAPH_ISO_BIN} -p ${FIXR_GRAPH_PYTHON}/scheduler/run_iso.py -l /tmp -t ${TIMEOUT} &>> ${OUT_LOG}
check_res "$?" "Scheduling isomorphisms"

pushd .
cd ${OUT_DIR}/out_jobs
echo "Computing isomorphisms..."
make -f scheduler_iso_index.make &>> ${OUT_LOG}
popd

echo "Processing logs..."
python ${FIXR_GRAPH_PYTHON}/db/scripts/process_logs.py  -s ${OUT_DIR}/out_jobs/scheduler_iso_index.make -j ${OUT_DIR}/out_jobs -n ${OUT_DIR}/out_jobs -g ${OUT_DIR}/graphs -g ${OUT_DIR}/graphs -o ${OUT_DIR}/graphs_db.db &>> ${OUT_LOG}
check_res "$?" "Processing logs"

echo "Generating html pages..."
python ${FIXR_GRAPH_PYTHON}/provenance/gen_html.py -d ${OUT_DIR}/graphs_db.db -o ${OUT_DIR}/index -g ${OUT_DIR}/graphs -p ${OUT_DIR}/provenance -i ${OUT_DIR}/iso &>> ${OUT_LOG}
check_res "$?" "Generating html pages"


echo "Running community detection..."
# Generate the list of isomorphisms
echo "Extracting isomorphism..."
python ${FIXR_GRAPH_PYTHON}/db/scripts/filter_isos.py -d ${OUT_DIR}/graphs_db.db -o ${OUT_DIR}/iso_list.txt -w 10
# Run the community detection
echo "Computing communities..."
echo "${SPARK_SUBMIT_PATH} --class edu.colorado.plv.fixr.community.Main ${FIXR_COMMUNITY_DETECTION_JAR} -w iso -i ${OUT_DIR}/iso -f ${OUT_DIR}/iso_list.txt -o ${OUT_DIR}/communities"
${SPARK_SUBMIT_PATH} --class edu.colorado.plv.fixr.community.Main ${FIXR_COMMUNITY_DETECTION_JAR} -w iso -i ${OUT_DIR}/iso -f ${OUT_DIR}/iso_list.txt -o ${OUT_DIR}/communities


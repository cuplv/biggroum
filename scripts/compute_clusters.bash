#!/bin/bash
# Script used to compute the clusters
#
# The script does the following:
# A. Find the acdfg files in the filesToItemSetCluster folder
# B. Run the frequent itemset computation
# C. Compute the cluster
#   C1. Generate the cluster files and the makefile
#   C2. Compute the cluster
# D. Computes the HTML output
#

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
check_exists "${config_script}" "config.bash script was not provided!"
source ${config_script}

check_exists "${FIXR_GRAPH_ISO}" "FixrGraphIso binary"
FIXR_GRAPH_FREQUENTITEMSET_BIN="$(readlink -f ${FIXR_GRAPH_ISO}/build/src/fixrgraphiso/frequentitemsets)"
FIXR_GRAPH_FREQUENTSUBGRAPHS_BIN="$(readlink -f ${FIXR_GRAPH_ISO}/build/src/fixrgraphiso/frequentsubgraphs)"
FIXR_GRAPH_PROCESS_CLUSTERS="$(readlink -f ${FIXR_GRAPH_ISO}/scripts/processClusters.py)"
FIXR_GRAPH_GATHER_RESULTS="$(readlink -f ${FIXR_GRAPH_ISO}/scripts/gatherResults.py)"
FIXR_GRAPH_PYTHON="$(readlink -f "${script_dir}/../python/fixrgraph/")"

GEN_MAKE_ISO="${script_dir}/gen_make_iso.py"
check_exists "${GEN_MAKE_ISO}" "Gen iso script"

check_exists "${FIXR_GRAPH_FREQUENTITEMSET_BIN}" "FIXR_GRAPH_FREQUENTITEMSET_BIN"
check_exists "${FIXR_GRAPH_FREQUENTSUBGRAPHS_BIN}" "FIXR_GRAPH_FREQUENTSUBGRAPHS_BIN"
check_exists "${FIXR_GRAPH_PROCESS_CLUSTERS}" "FIXR_GRAPH_PROCESS_CLUSTERS"
check_exists "${FIXR_GRAPH_GATHER_RESULTS}" "FIXR_GRAPH_GATHER_RESULTS"
check_exists "${FIXR_GRAPH_PYTHON}" "FIXR_GRAPH_PYTHON"

if [ ! -d "${OUT_DIR}" ] ; then
    echo "${OUT_DIR} does not exists!"
    exit 1
fi
OUT_LOG=${OUT_DIR}/out_log.txt

CLUSTER_DIR="$(readlink -f "${OUT_DIR}/clusters")"
if [ -d "${CLUSTER_DIR}" ] ; then
    echo "${CLUSTER_DIR} already exists!"
    exit 1
else
    mkdir -p "${CLUSTER_DIR}"    
fi


ITEMSET_FILE=${CLUSTER_DIR}/filesToItemSetCluster
CLUSTER_FILE=${CLUSTER_DIR}/clusters.txt
ALL_CLUSTERS=${CLUSTER_DIR}/all_clusters
mkdir ${ALL_CLUSTERS}


total=4

# A. Find the acdfg files in the filesToItemSetCluster folder
echo "1/${total} Find the acdfgs..."
echo "python ${FIXR_GRAPH_PYTHON}/db/scripts/get_graphs_list.py -d ${OUT_DIR}/graphs_db.db -r ${OUT_DIR}/graphs -o ${ITEMSET_FILE}"
python ${FIXR_GRAPH_PYTHON}/db/scripts/get_graphs_list.py -d ${OUT_DIR}/graphs_db.db -r ${OUT_DIR}/graphs -o ${ITEMSET_FILE}
check_res "$?" "Find acdfg"

# B. Run the frequent itemset computation
echo "2/${total} Compute the frequent itemset..."
echo "${FIXR_GRAPH_FREQUENTITEMSET_BIN} -f ${FREQ_CUTOFF} -m ${MIN_METH}  -o ${CLUSTER_FILE} ${ITEMSET_FILE}"
${FIXR_GRAPH_FREQUENTITEMSET_BIN} -f ${FREQ_CUTOFF} -m ${MIN_METH} -o ${CLUSTER_FILE} ${ITEMSET_FILE}
# Frequent itemset computation always returns an error code
# check_res "$?" "Compute frequent itemset"

# C. Compute the cluster
# C1. Generate the cluster files and the makefile
# C2. Compute the cluster 
echo "python ${GEN_MAKE_ISO} -f ${FREQ_CUTOFF} -m ${MIN_METH} -d ${OUT_DIR} -t 18000 -p ${FIXR_GRAPH_PROCESS_CLUSTERS} -g ${FIXR_GRAPH_ISO}"
python ${GEN_MAKE_ISO} -f ${FREQ_CUTOFF} -m ${MIN_METH} -d ${OUT_DIR} -t 18000 -p ${FIXR_GRAPH_PROCESS_CLUSTERS} -g ${FIXR_GRAPH_ISO}
check_res "$?" "Generate cluster files"

# C2. Computes clusters
echo "3/${total} Compute the clusters (it may take a while)..."
makefile="${OUT_DIR}/makefile"
pushd .
echo "cd ${OUT_DIR}"
cd ${OUT_DIR}
make -f ${makefile}
popd
echo "Computed clusters"

# D. Computes the HTML output
echo "4/${total} Compute the html output"
pushd ${CLUSTER_DIR}
mkdir html_files
nclusters=`cat ${CLUSTER_FILE}  | grep "I:" | wc -l` && nclusters=$((nclusters)); echo $nclusters
echo "python ${FIXR_GRAPH_GATHER_RESULTS}  -a 1 -b ${nclusters} -o html_files -i all_clusters -p ${OUT_DIR}/provenance"
python ${FIXR_GRAPH_GATHER_RESULTS}  -a 1 -b ${nclusters} -o html_files -i all_clusters -p ${OUT_DIR}/provenance
echo "Generating png files..."
for f in `find . -name "*.dot"`; do app=`echo ${f} | sed "s:\.dot:.png:"`; dot -Tpng -o$app $f; done
popd
echo "Computed the html output"


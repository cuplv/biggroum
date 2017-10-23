"""
Handles the computation of clusters and patterns
"""

import os

class Clusters:

    CMD_GRAPHISO="""
    #!/bin/bash

    rl="$(readlink -f "$0")"
    script_dir="$(dirname "${rl}")"

    if [ "${START_RANGE}X" == "X" ]; then
      echo "START_RANGE variable not set"
      exit 1
    fi

    if [ "${END_RANGE}X" == "X" ]; then
      echo "END_RANGE variable not set"
      exit 1
    fi


    date
    pushd .
    cd ${script_dir}/../../

    echo "time -p (ulimit -t ${TIMEOUT}; python3 ${PROCESS_CLUSTER_SCRIPT} -n -c ./clusters.txt -d ./all_clusters -a ${START_RANGE} -b ${END_RANGE} -p ${GRAPH_ISO_PATH})"

    time -p (ulimit -t ${TIMEOUT}; python3 ${PROCESS_CLUSTER_SCRIPT} -n -c ./clusters.txt -d ./all_clusters -a ${START_RANGE} -b ${END_RANGE} -p ${GRAPH_ISO_PATH})

    popd

    date

    """

    
    """
    Read the cluster file and returns a list of clusters.

    Input:
    - cluster_file: path to the cluster file
    Output:
    - cluster_list: a list of tuples containing the cluster id, the
    list of methods in the cluster, the length of the acdfg list in
    the cluster, the list of acdfgs. 
    """

    @staticmethod
    def read_clusters(cluster_file):
        cluster_list = []

        count = 0
        method_list = None
        acdfg_list = None
        with open(cluster_file, 'r') as cf:
            for line in cf.readlines():
                if (line.startswith("I:")):
                    count = count + 1
                    assert method_list is None
                    assert acdfg_list is None
                    method_line = line[len("I:"):].strip()
                    method_list = method_line[:method_line.index("(")]
                    total_methods = method_line[method_line.index("("):]
                    total_methods = total_methods.replace("( ","")
                    total_methods = total_methods.replace(" )","")
                    acdfg_list = []
                elif (line.startswith("F:")):
                    assert acdfg_list is not None
                    acdfg_list.append(line[len("F:"):].strip())
                elif (line.startswith("E")):
                    assert str(len(acdfg_list)) == total_methods
                    cluster_list.append((count, method_list, len(acdfg_list), acdfg_list))
                    method_list = None
                    acdfg_list = None

            cf.close()

        # wf file has an end
        assert method_list is None
        assert acdfg_list is None

        return cluster_list

    """
    Generate a makefile to run the pattern computation

    - makefile: path to the makefile to be created
    - base_cluster_path: path to the clusters directory
    - timeout: timeout for the compuatation of a single cluster
    - graphisopath: path to the FixrGraphIso project
    """
    @staticmethod
    def gen_make(makefile,
                 base_cluster_path,
                 timeout, # timeout to compute the patter for a cluster
                 graphisopath, # path 
                 processcluster):
        def get_cluster_list(base_cluster_path):
            cluster_path = os.path.join(base_cluster_path, "all_clusters")
            clusters = []
            for root, subFolders, files in os.walk(cluster_path):
                for folder in subFolders:
                    if folder.startswith("cluster_"):
                        cluster_id = folder[(folder.index("_")+1):]
                        clusters.append((os.path.join("all_clusters", folder), cluster_id))
                break
            return clusters

        def get_suffix_name(to):
            suffix = "_%s" % (to)
            return suffix

        suffix = get_suffix_name(timeout)
        with open(makefile, "w") as f:
            clusters = get_cluster_list(base_cluster_path)
            tasks = ["cluster_%s" % clusterid for (cluster,clusterid) in clusters]
            target_string = " ".join(tasks)
            f.write("ALL: %s\n\t\n" % (target_string))

            for (cluster,clusterid) in clusters:
                params = {"TIMEOUT" : timeout,
                          "CLUSTER_BASE_FOLDER" : base_cluster_path,
                          "PROCESS_CLUSTER_SCRIPT" : processcluster,
                          "GRAPH_ISO_PATH" : graphisopath,
                          "START_RANGE" : str(clusterid),
                          "END_RANGE" : str(clusterid)}
                script_data = _substitute(Clusters.CMD_GRAPHISO, params)
                script_file = os.path.join(base_cluster_path, cluster, "run_graph_%ss.bash" % (suffix))

                with open(script_file, "w") as fs:
                    fs.write("%s" % script_data)
                    fs.close()

                target_name = "cluster_%s" % clusterid
                rel_script_file = os.path.join(base_cluster_path.split("/")[-1], cluster, os.path.basename(script_file))

                output = rel_script_file + ".out"

                f.write("%s: \n\tbash './%s'\n\n" % (target_name, rel_script_file))
            f.close()


    """
    Generate the cluster folders used to compute the frequent patterns.

    - graphiso_cluster_path: path to the clusters directory
    - cluster_file: path to the file containing the clusters
    """
    @staticmethod
    def generate_graphiso_clusters(graphiso_cluster_path,
                                   cluster_file):
        # read each cluster, creating a folder for each of them
        for (cluster_id, method_list, tot, acdfg_list) in Clusters.read_clusters(cluster_file):
            dst_path = os.path.join(graphiso_cluster_path, "all_clusters",
                                    "cluster_%d" % cluster_id)
            os.makedirs(dst_path)
            for acdfg in acdfg_list:
                dst_file = os.path.join(dst_path, os.path.basename(acdfg))
                os.symlink(acdfg, dst_file)
    

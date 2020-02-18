"""
Handles the computation of clusters and patterns
"""

import os
import string

class Clusters:

    CMD_BUILD_ACDFG_LIST="""find ${CLUSTER_PATH} -name "*acdfg.bin" > ${ACDFG_LIST_FILE}"""
    CMD_FOR_MAKE="""time -p sh -c 'ulimit -t ${TIMEOUT}; ${FIXRGRAPHISOBIN} -f ${FREQUENCY} ${REL_FREQ_PARAMS} -m ${CLUSTER_PATH}/methods_${CLUSTER_ID}.txt -p ${CLUSTER_PATH} -o ${CLUSTER_PATH}/cluster_${CLUSTER_ID}_info.txt -l ${CLUSTER_PATH}/cluster_${CLUSTER_ID}_lattice.bin ${IS_ANYTIME} -i ${ACDFG_LIST_FILE} > ${CLUSTER_PATH}/run1.out 2> ${CLUSTER_PATH}/run1.err.out; echo "Computed cluster ${CLUSTER_ID}"'; echo "Computed cluster ${CLUSTER_ID}"
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
                    method_s = method_line[:method_line.index("(")]
                    method_list = [s.strip() for s in method_s.split(",")]
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
    Generate a makefile to run the pattern computation inside the
    base_cluster_path.

    - base_cluster_path: path to the clusters directory
    - timeout: timeout for the compuatation of a single cluster
    - graphisopath: path to the FixrGraphIso project
    """
    @staticmethod
    def gen_make(base_cluster_path,
                 timeout, # timeout to compute the patter for a cluster
                 frequency_cutoff,
                 graphisopath, # path
                 frequentsubgraph_path,
                 use_relative_frequency = False,
                 relative_frequency = 0.1,
                 is_anytime = False):
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

        makefile = os.path.join(base_cluster_path, "makefile")
        suffix = get_suffix_name(timeout)
        with open(makefile, "w") as f:
            clusters = get_cluster_list(base_cluster_path)
            tasks = ["cluster_%s" % clusterid for (cluster,clusterid) in clusters]
            target_string = " ".join(tasks)
            f.write("ALL: %s\n\t\n" % (target_string))

            for (cluster,clusterid) in clusters:

                if (not use_relative_frequency):
                  rel_req_param = ""
                else:
                  rel_req_param = "-r %f" % relative_frequency

                cluster_path = os.path.join(base_cluster_path,
                                            "all_clusters",
                                            "cluster_%s" % clusterid)
                acdfg_list_file = os.path.join(cluster_path,
                                               "all_acdfg_bin.txt")

                if is_anytime:
                    is_anytime_params = "-a -s"
                else:
                    is_anytime_params = ""

                acdfg_params = {"CLUSTER_PATH" : cluster_path,
                                "ACDFG_LIST_FILE" : acdfg_list_file}
                params = {"TIMEOUT" : timeout,
                          "FREQUENCY" : frequency_cutoff,
                          "CLUSTER_PATH" : cluster_path,
                          "ACDFG_LIST_FILE" : acdfg_list_file,
                          "CLUSTER_ID" : str(clusterid),
                          "FIXRGRAPHISOBIN" : frequentsubgraph_path,
                          "REL_FREQ_PARAMS" : rel_req_param,
                          "IS_ANYTIME" : is_anytime_params}

                acdfg_list_cmd = string.Template(Clusters.CMD_BUILD_ACDFG_LIST).safe_substitute(acdfg_params)
                comp_cmd = string.Template(Clusters.CMD_FOR_MAKE).safe_substitute(params)
                target_name = "cluster_%s" % clusterid
                f.write("%s:\n\t%s\n\t%s\n\n" % (target_name, acdfg_list_cmd, comp_cmd))
            f.close()


    """
    Generate the cluster folders used to compute the frequent patterns.

    - graphiso_cluster_path: path to the clusters directory
    - cluster_file: path to the file containing the clusters
    """
    @staticmethod
    def generate_graphiso_clusters(graphiso_cluster_path,
                                   cluster_file):
        # read each cluster, creating a folder for each of them and the methods file
        for (cluster_id, method_list, tot, acdfg_list) in Clusters.read_clusters(cluster_file):

            # Create the destination directory
            dst_path = os.path.join(graphiso_cluster_path, "all_clusters",
                                    "cluster_%d" % cluster_id)
            os.makedirs(dst_path)

            # Create a symlink to all the groums
            for acdfg in acdfg_list:
                dst_file = os.path.join(dst_path, os.path.basename(acdfg))

                try:
                    os.symlink(acdfg, dst_file)
                except OSError as e:
                    print("Error creating the symlink %s -> %s" % (acdfg, dst_file))
                    raise e

            # Create the methods file
            method_file = os.path.join(dst_path, 'methods_%d.txt' % cluster_id)
            with open(method_file, 'wt') as method_f:
                for s in method_list:
                    method_f.write("%s\n" % s)
                method_f.close()



# Create the make files that run the different experimental evaluation
# ...
#
import string
import os
import logging
import sys
import subprocess
import shutil
import optparse
import tempfile
import optparse

def _substitute(template, substitution):
    return string.Template(template).safe_substitute(substitution)


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

def generate_graphiso_clusters(graphiso_cluster_path,
                               cluster_file,
                               freq_cutoff, min_node):
    # read each cluster, creating a folder for each of them
    for (cluster_id, method_list, tot, acdfg_list) in read_clusters(cluster_file):
        dst_path = os.path.join(graphiso_cluster_path, "all_clusters",
                                "cluster_%d" % cluster_id)
        os.makedirs(dst_path)
        for acdfg in acdfg_list:
            dst_file = os.path.join(dst_path, os.path.basename(acdfg))
            os.symlink(acdfg, dst_file)

# WRAP SRIRAM's SCRIPT
cmd_graphiso="""
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




def get_cluster_list(path):
    cluster_path = os.path.join(path, "all_clusters")

    clusters = []
    for root, subFolders, files in os.walk(cluster_path):
        for folder in subFolders:
            if folder.startswith("cluster_"):

                cluster_id = folder[(folder.index("_")+1):]
                clusters.append((os.path.join("all_clusters", folder), cluster_id))

        break

    return clusters


def gen_make(makefile, path, freq_cutoff, min_node, timeout,
             graphisopath, processcluster):
    suffix = get_suffix_name(freq_cutoff, min_node, timeout)
    with open(makefile, "w") as f:
        clusters = get_cluster_list(path)
        tasks = ["cluster_%s" % clusterid for (cluster,clusterid) in clusters]
        target_string = " ".join(tasks)
        f.write("ALL: %s\n\t\n" % (target_string))

        for (cluster,clusterid) in clusters:
            params = {"PROCESS_CLUSTER_SCRIPT" : "${PROCESS_CLUSTER_SCRIPT}",
                      "TIMEOUT" : timeout,
                      "CLUSTER_BASE_FOLDER" : path,
                      "PROCESS_CLUSTER_SCRIPT" : processcluster,
                      "GRAPH_ISO_PATH" : graphisopath,
                      "START_RANGE" : str(clusterid),
                      "END_RANGE" : str(clusterid)}
            script_data = _substitute(cmd_graphiso, params)
            script_file = os.path.join(path, cluster, "run_graph_%ss.bash" % (suffix))

            with open(script_file, "w") as fs:
                fs.write("%s" % script_data)
                fs.close()

            target_name = "cluster_%s" % clusterid
            rel_script_file = os.path.join(path.split("/")[-1], cluster, os.path.basename(script_file))

            output = rel_script_file + ".out"

            f.write("%s: \n\tbash './%s'\n\n" % (target_name, rel_script_file))
        f.close()

        print "Created %s" % makefile


def get_suffix_name(freq_cutoff, min_node, to):
    suffix = "_%s_%s_%s" % (freq_cutoff, min_node, to)
    return suffix



def generate_make_file(dataset_path, freq_cutoff, min_node, to,
                       graphisopath, processcluster):
    graphiso_cluster_path = os.path.join(dataset_path, "clusters")

    to_process = [graphiso_cluster_path]
    for path in to_process:
        # suffix = get_suffix_name(freq_cutoff, min_node, to)
        gen_make(os.path.join(dataset_path, "makefile"),
#                              "makefile_" + os.path.basename(path) + suffix),
                 path, freq_cutoff, min_node, to,
                 graphisopath, processcluster)

def main():
    p = optparse.OptionParser()
    p.add_option('-d', '--extractiondir', help="base extraction directory")
    p.add_option('-p', '--processcluster', help="processCluster.py script")
    p.add_option('-g', '--graphisopath', help="graphisopath")
    p.add_option('-f', '--freqcutoff', help="Frequency cutoff")
    p.add_option('-m', '--minnode', help="Min node")
    p.add_option('-t', '--timeout', help="Timeout")
    opts, args = p.parse_args()

    def usage(msg=""):
        if msg:
            print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)

    if (not opts.extractiondir): usage("No extraction directory")
    if (not os.path.isdir(opts.extractiondir)):
        usage("%s is not a directory" % opts.extractiondir)
    if (not opts.graphisopath): usage("No graphiso directory")
    if (not os.path.isdir(opts.graphisopath)):
        usage("%s is not a directory" % opts.graphisopath)

    if (not opts.processcluster): usage("No procesclusterpath")
    if (not os.path.isfile(opts.processcluster)):
        print(os.path.isfile(opts.processcluster))
        usage("%s does notexists" % opts.processcluster)

    if (not opts.freqcutoff): usage("No freq cutoff")
    try:
        int(opts.freqcutoff)
        freqcutoff = opts.freqcutoff
    except:
        usage("No freq cutoff is not an int")

    if (not opts.minnode): usage("No freq cutoff")
    try:
        int(opts.minnode)
        minnode= opts.minnode
    except:
        usage("No freq cutoff is not an int")
    if (not opts.timeout): usage("No timeout")
    try:
        int(opts.timeout)
        timeout = opts.timeout
    except:
        usage("No timeout provided")

    cluster_path = os.path.join(opts.extractiondir,
                                "clusters")
    cluster_file = os.path.join(cluster_path,
                                "clusters.txt")
    generate_graphiso_clusters(cluster_path,
                               cluster_file,
                               freqcutoff,
                               timeout)

    generate_make_file(opts.extractiondir,
                       freqcutoff, minnode, timeout,
                       opts.graphisopath,
                       opts.processcluster)


if __name__ == '__main__':
    main()


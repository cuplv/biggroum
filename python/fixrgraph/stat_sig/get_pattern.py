import os
import sys
import logging
import traceback

from fixrgraph.annotator.protobuf.proto_acdfg_pb2 import Acdfg
from google.protobuf.json_format import MessageToJson
from fixrgraph.solr.patterns_utils import parse_clusters, parse_cluster_info

def get_pattern(graph_path, method_list, out_path):
    proto_acdfg = None
    with open(graph_path) as groum_file:
        proto_acdfg = Acdfg()
        proto_acdfg.ParseFromString(groum_file.read())
        groum_file.close()


    # lookup...
    all_nodes = {}
    is_data = set()
    is_misc = set()
    is_method = set()
    nodes = [(proto_acdfg.data_node, is_data),
             (proto_acdfg.misc_node, is_misc),
             (proto_acdfg.method_node, is_method)]
    for (node_list, ids_set) in nodes:
        for node in node_list:
            all_nodes[node.id] = node
            ids_set.add(node.id)

    # get method nodes IDs that must stay
    important_ids = set()
    for method_node in proto_acdfg.method_node:
        if method_node.name in method_list:
            important_ids.add(method_node.id)

    def insert_node(out_acdfg,
                    node,
                    is_data, is_misc, is_method,
                    id_inserted_node):

        if node.id in id_inserted_node:
            return

        if (node.id in is_data):
            new_node = out_acdfg.data_node.add()
            new_node.name = node.name
            new_node.type = node.type
            if node.HasField("data_type"):
                new_node.data_type = node.data_type
        elif (node.id in is_misc):
            new_node = out_acdfg.misc_node.add()
        elif (node.id in is_method):
            new_node = out_acdfg.method_node.add()
            new_node.name = node.name
            if (node.HasField("assignee")):
                new_node.assignee = node.assignee
            if (node.HasField("invokee")):
                new_node.invokee = node.invokee

            for arg in node.argument:
                new_node.argument.append(arg)
        else:
            raise Exception("Unknown type!")

        new_node.id = node.id
        id_inserted_node.add(new_node.id)

    # Create the out acdfgs
    out_acdfg = Acdfg()

    id_inserted_node = set()
    edges = [proto_acdfg.control_edge,
             proto_acdfg.def_edge,
             proto_acdfg.use_edge,
             proto_acdfg.trans_edge,
             proto_acdfg.exceptional_edge]

    for edge_list in edges:
        for edge in edge_list:
            from_id = getattr(edge, 'from')
            to_id = edge.to

            at_least_one = (from_id in important_ids or to_id in important_ids)
            inv_misc = from_id in is_misc or to_id in is_misc
            enforce =  (
                ((not from_id in is_method) or from_id in important_ids) and
                ((not to_id in is_method) or to_id in important_ids)
            )

            if (at_least_one and enforce and (not inv_misc)):
                insert_node(out_acdfg,
                            all_nodes[from_id],
                            is_data, is_misc, is_method,
                            id_inserted_node)

                insert_node(out_acdfg,
                            all_nodes[to_id],
                            is_data, is_misc, is_method,
                            id_inserted_node)

                new_edge = out_acdfg.control_edge.add()
                new_edge.id = edge.id
                setattr(new_edge, 'from', from_id)
                new_edge.to = to_id

    f = open(out_path, "wb")
    f.write(out_acdfg.SerializeToString())
    f.close()



out_path = "/home/sergio/works/projects/muse/pattern_repr"
cluster_path = ""
root = "/home/sergio/Downloads/SANER/SANER_SHARED/SANER_ARTIFACT/results/computed_patterns/graphiso/"

cinfo_file = os.path.join(root, "all_clusters.txt")

with open(cinfo_file, 'r') as f:
    cluster_infos = parse_clusters(f)
    f.close()

for cluster_info in cluster_infos:
    print "Processing cluster %d/%d" % (cluster_info.id, len(cluster_infos))

    cluster_path = os.path.join(root,
                                "all_clusters/cluster_%d" % cluster_info.id)
    cluster_info_file = os.path.join(cluster_path,
                                     "cluster_%d_info.txt" % cluster_info.id)

    if os.path.isfile(cluster_info_file):
        with open(cluster_info_file, 'r') as f:
            pattern_list = parse_cluster_info(f)
            f.close()

        for pattern in pattern_list:
            print "Processing pattern %s/%d" % (pattern.id, len(pattern_list))

            assert(len(pattern.groum_files_list) > 0)
            out_file = os.path.join(out_path,
                                    "%d_%s_%s.acdfg.bin" % (cluster_info.id,
                                                            pattern.type,
                                                            pattern.id))

            gfile = os.path.join(cluster_path, pattern.groum_files_list[0])
            try:
                get_pattern(gfile,
                            cluster_info.methods_list,
                            out_file)
            except:
                traceback.print_exc()
    else:
        logging.info("Cluster not computed %s" % cluster_info_file)


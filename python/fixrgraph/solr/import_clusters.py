import sys
import os
import optparse
import logging
import string
import collections
import re

import pysolr

from fixrgraph.annotator.protobuf import proto_acdfg_pb2
from fixrgraph.solr.common import MissingProtobufField
from fixrgraph.solr.common import upload_pool
from fixrgraph.solr.import_graphs import get_id as get_groum_key
from fixrgraph.solr.import_graphs import check_field, get_repo_sni
from fixrgraph.solr.patterns_utils import ClusterInfo, parse_clusters
from fixrgraph.solr.import_patterns import _get_cluster_key, _get_groum_key_from_bin, _create_pattern_docs


def _get_cluster_doc(cluster_info, patterns_keys_list):
    cluster_doc = {}
    cluster_doc["doc_type_sni"] = "cluster"
    cluster_doc["id"] = _get_cluster_key(cluster_info.id)
    cluster_doc["patterns_keys_t"] = patterns_keys_list
    cluster_doc["methods_in_cluster_t"] = cluster_info.methods_list
    groum_keys = []
    i = 0
    for groum_file in cluster_info.groum_files_list:
        i = i + 1
        logging.info("Getting key %d/%d" % (i, len(cluster_info.groum_files_list)))
        if os.path.isfile(groum_file):
            groum_key = _get_groum_key_from_bin(groum_file)
            groum_keys.append(groum_key)
        else:
            logging.info("%s does not exist %s" % groum_file)
    cluster_doc["groum_keys_t"] = groum_keys

    return cluster_doc

def main():
    logging.basicConfig(level=logging.DEBUG)

    p = optparse.OptionParser()
    p.add_option('-c', '--cluster_dir', help="Base path containing the clusters")
    p.add_option('-f', '--cluster_file', help="Name of the cluster file " +
                 "(default: clusters.txt)")
    p.add_option('-i', '--cluster_id', help="Cluster id to import")
    p.add_option('-s', '--solr_url', help="URL to solr")

    def usage(msg=""):
        if msg:
            print "----%s----\n" % msg
        p.print_help()
        print "Example of usage %s" % ("python import_clusters.py  "
                                       "-c /tmp/testextraction/clusters "
                                       "-s  'http://localhost:8983/solr/groums'")
        sys.exit(1)

    opts, args = p.parse_args()
    if (not opts.solr_url): usage("Solr URL not provided!")

    paths = [(opts.cluster_dir, "Cluster dir")]
    for (path,msg) in paths:
        if (not path): usage("%s not provided!" % msg)
        if (not os.path.isdir(path)): usage("%s %s does "
                                            "not exist!" % (msg,path))
    if (opts.cluster_file):
        cluster_file_name = opts.cluster_file
    else:
        cluster_file_name = "clusters.txt"

    solr = pysolr.Solr(opts.solr_url)
    doc_pool = []
    threshold = 10000

    cluster_file = os.path.join(opts.cluster_dir, cluster_file_name)
    with open(cluster_file, "r") as f:
        logging.info("Parsing file %s" % cluster_file)
        clusters_info_list = parse_clusters(f)

        try:
            for cluster_info in clusters_info_list:

                if opts.cluster_id:
                    if str(cluster_info.id) != str(opts.cluster_id):
                        continue

                logging.info("Processing cluster %d" % cluster_info.id)

                current_path = os.path.join(opts.cluster_dir,
                                            "all_clusters",
                                            "cluster_%d" % cluster_info.id)
                cluster_info_file = os.path.join(current_path,
                                                 "cluster_%d_info.txt" % cluster_info.id)

                pattern_keys_list = []
                if (os.path.isfile(cluster_info_file)):
                    pattern_docs = _create_pattern_docs(current_path,
                                                        cluster_info_file)
                    logging.info("Adding %d patterns" %  len(pattern_docs))
                    for pattern in pattern_docs:
                        doc_pool.append(pattern)
                        pattern_keys_list.append(pattern["id"])
                else:
                    logging.warning("Cluster info file not found: %s" % cluster_info_file)

                cluster_doc = _get_cluster_doc(cluster_info, pattern_keys_list)
                doc_pool.append(cluster_doc)
                doc_pool = upload_pool(solr, threshold, doc_pool)
            doc_pool = upload_pool(solr, -1, doc_pool)
        except MissingProtobufField as e:
            logging.warn("Missing field for %s (%s)" % (name, relpath))

        f.close()


if __name__ == '__main__':
    main()

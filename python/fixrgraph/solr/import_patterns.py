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
from fixrgraph.solr.patterns_utils import PatternInfo, parse_cluster_info

def _get_pattern_key(cluster_id, pattern_id, pattern_type):
    key = "%s/%s/%s" % (cluster_id, pattern_type,  pattern_id)
    return key

def _get_cluster_key(cluster_id):
    key = "%s" % (cluster_id)
    return key

def _get_groum_key_from_bin(acdfg_path):
    with open(acdfg_path, "rb") as acdfg_file:
        acdfg = proto_acdfg_pb2.Acdfg()
        acdfg.ParseFromString(acdfg_file.read())

        check_field(acdfg.repo_tag, "repo_name")
        check_field(acdfg.repo_tag, "user_name")
        check_field(acdfg.repo_tag, "commit_hash")

        repo_name = acdfg.repo_tag.repo_name
        user_name = acdfg.repo_tag.user_name
        class_name = acdfg.source_info.class_name
        method_name = acdfg.source_info.method_name
        hash_sni = acdfg.repo_tag.commit_hash

        repo_sni = get_repo_sni(user_name, repo_name)
        groum_key = get_groum_key(repo_sni, hash_sni, class_name, method_name)

        acdfg_file.close()

        return groum_key

def _create_pattern_docs(current_path, cluster_info_path):
    pattern_doc_list = []

    cluster_id_re= re.match(r".*cluster_(\d+)$",current_path)
    if cluster_id_re is not None:
        cluster_id = cluster_id_re.group(1)
    else:
        logging.warn("Cannot find cluster id from %s" % current_path)
        cluster_id = -1

    # Read the pattern info
    with open(cluster_info_path, 'r') as f:
        pattern_info_list = parse_cluster_info(f)
        f.close()

    for pattern_info in pattern_info_list:
        pattern_doc = {}
        pattern_doc["doc_type_sni"] = "pattern"
        pattern_doc["id"] = _get_pattern_key(cluster_id,
                                             pattern_info.id,
                                             pattern_info.type)
        pattern_doc["cluster_key_sni"] = _get_cluster_key(cluster_id)
        pattern_doc["type_sni"] = pattern_info.type
        pattern_doc["frequency_sni"] = pattern_info.frequency

        groum_keys_list = []
        for groum in pattern_info.groum_files_list:
            acdfg_path = os.path.join(current_path, groum)
            groum_key = _get_groum_key_from_bin(acdfg_path)
            groum_keys_list.append(groum_key)

        pattern_doc["groum_keys_t"] = groum_keys_list

        assert pattern_info.dot_name is not None
        dot_path = os.path.join(current_path, pattern_info.dot_name)
        with open(dot_path, 'r') as dot_file:
            pattern_doc["groum_dot_sni"] = dot_file.read()

        pattern_doc_list.append(pattern_doc)

    return pattern_doc_list

def main():
    logging.basicConfig(level=logging.DEBUG)

    p = optparse.OptionParser()
    p.add_option('-c', '--cluster_dir', help="Base path containing the clusters")
    p.add_option('-s', '--solr_url', help="URL to solr")

    def usage(msg=""):
        if msg:
            print "----%s----\n" % msg
        p.print_help()
        print "Example of usage %s" % ("python import_graphs.py  "
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

    solr = pysolr.Solr(opts.solr_url)
    doc_pool = []
    threshold = 10000

    name_pattern = re.compile("cluster_(\d+)_info.txt")

    for root, dirs, files in os.walk(opts.cluster_dir):
        for name in files:
            res_match = name_pattern.match(name)
            if res_match is not None:
                pattern_id = res_match.group(1)
                cluster_info_path = os.path.join(root, name)

                try:
                    current_path = os.path.dirname(cluster_info_path)
                    pattern_docs = _create_pattern_docs(current_path,
                                                        cluster_info_path)
                    doc_pool.extend(pattern_docs)
                except MissingProtobufField as e:
                    logging.warn("Missing field for %s (%s)" % (name, relpath))
                except IOError as e:
                    logging.warn("Error reading file %s" % (e.filename))

                doc_pool = upload_pool(solr, threshold, doc_pool)
    doc_pool = upload_pool(solr, -1, doc_pool)

if __name__ == '__main__':
    main()

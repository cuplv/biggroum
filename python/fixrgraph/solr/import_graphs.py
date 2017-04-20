# Import the GROUM documents in Solr
#

import sys
import os
import optparse
import logging
import string
import collections

from fixrgraph.annotator.protobuf import proto_acdfg_pb2
import pysolr

class MissingProtobufField(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

def _create_groum_doc(acdfg_path, provenance_path):
    def get_id(repo_sni, class_name_t, method_name_t):
        key = "%s/%s/%s" % (repo_sni, class_name_t, method_name_t)
        return key

    def get_repo_sni(user_name, repo_name):
        repo_sni = "%s/%s" % (user_name, repo_name)
        return repo_sni

    def check_field(proto, field):
        if not proto.HasField(field):
            raise MissingProtobufField("Missing field %s in "
                                       "the protobuffer file" % field)

    def fill_from_acdfg(groum_doc, acdfg_path):
        with open(acdfg_path, "rb") as acdfg_file:
            acdfg = proto_acdfg_pb2.Acdfg()
            acdfg.ParseFromString(acdfg_file.read())

            check_field(acdfg, "repo_tag")
            check_field(acdfg.repo_tag, "repo_name")
            check_field(acdfg.repo_tag, "user_name")
            check_field(acdfg.repo_tag, "commit_hash")

            repo_name = acdfg.repo_tag.repo_name
            user_name = acdfg.repo_tag.user_name
            groum_doc["repo_sni"] = get_repo_sni(user_name, repo_name)

            groum_doc["hash_sni"] = acdfg.repo_tag.commit_hash

            if (acdfg.repo_tag.HasField("url")):
                groum_doc["github_url_sni"] = acdfg.repo_tag.url

            check_field(acdfg, "source_info")
            source_info = acdfg.source_info
            check_field(source_info, "package_name")
            check_field(source_info, "class_name")
            check_field(source_info, "method_name")
            check_field(source_info, "source_class_name")

            groum_doc["package_name_sni"] = source_info.package_name
            groum_doc["class_name_t"] = source_info.class_name
            groum_doc["method_name_t"] = source_info.method_name
            groum_doc["filename_t"] = source_info.source_class_name

            if (source_info.HasField("class_line_number")):
                val = str(source_info.class_line_number)
                groum_doc["class_line_number_sni"] = val

            if (source_info.HasField("method_line_number")):
                val = str(source_info.method_line_number)
                groum_doc["method_line_number_sni"] = val

            acdfg_file.close()


    groum_doc = {}
    groum_doc["id"] = ""

    # From the acdfg.bin
    groum_doc["repo_sni"] = ""
    groum_doc["hash_sni"] = ""
    groum_doc["github_url_sni"] = ""

    # From the acdfg.bin
    groum_doc["filename_t"] = ""
    groum_doc["package_name_sni"] = ""
    groum_doc["class_name_t"] = ""
    groum_doc["method_name_t"] = ""
    groum_doc["class_line_number_sni"] = ""
    groum_doc["method_line_number_sni"] = ""

    # From the provenance
    groum_doc["groum_dot_sni"] = ""
    groum_doc["jimple_sni"] = ""

    fill_from_acdfg(groum_doc, acdfg_path)

    prefix = "%s_%s" % (groum_doc["class_name_t"],
                        groum_doc["method_name_t"])
    project_path = os.path.join(provenance_path,
                                groum_doc["repo_sni"],
                                groum_doc["hash_sni"])
    assert os.path.isdir(project_path)

    dot_file_name = os.path.join(project_path, "%s.acdfg.dot" % prefix)
    with open(dot_file_name, "r") as dot_file:
        groum_doc["groum_dot_sni"] = dot_file.read()
        dot_file.close()

    jimple_file_name = os.path.join(project_path, "%s.sliced.jimple" % prefix)
    with open(jimple_file_name, "r") as jimple_file:
        groum_doc["jimple_sni"] = jimple_file.read()
        jimple_file.close()

    groum_doc["id"] = get_id(groum_doc["repo_sni"],
                             groum_doc["class_name_t"],
                             groum_doc["method_name_t"])

    return groum_doc


def upload_pool(solr, threshold, doc_pool):
    if (len(doc_pool) >= threshold):
        logging.info("Uploading solr docs...")
        solr.add(doc_pool)
        doc_pool = []
    return doc_pool


def main():
    logging.basicConfig(level=logging.DEBUG)

    p = optparse.OptionParser()
    p.add_option('-g', '--graph_dir', help="Base path containing the graphs")
    p.add_option('-p', '--provenance_dir', help="Base path to the provenance info")
    p.add_option('-s', '--solr_url', help="URL to solr")

    def usage(msg=""):
        if msg:
            print "----%s----\n" % msg
        p.print_help()
        print "Example of usage %s" % ("python import_graphs.py  "
                                       "-g /tmp/testextraction/graphs "
                                       "-s  'http://localhost:8983/solr/groums'"
                                       "-p /tmp/testextraction/provenance/")
        sys.exit(1)
    opts, args = p.parse_args()

    if (not opts.solr_url): usage("Solr URL not provided!")

    paths = [(opts.graph_dir, "Graphs dir"),
             (opts.provenance_dir, "Provenance dir")]

    for (path,msg) in paths:
        if (not path): usage("%s not provided!" % msg)
        if (not os.path.isdir(path)): usage("%s %s does "
                                            "not exist!" % (msg,path))

    solr = pysolr.Solr(opts.solr_url)

    # Loop through the graph directory
    doc_pool = []
    threshold = 10000
    for root, dirs, files in os.walk(opts.graph_dir):
        for name in files:
            if name.endswith(".acdfg.bin"):
                # insert the graph
                real_path = os.path.join(root, name)
                try:
                    groum_doc = _create_groum_doc(real_path, opts.provenance_dir)
                    doc_pool.append(groum_doc)
                except MissingProtobufField as e:
                    logging.warn("Missing field for %s (%s)" % (name, relpath))
                except IOError as e:
                    logging.warn("Error reading file %s" % (e.filename))

                doc_pool = upload_pool(solr, threshold, doc_pool)
    doc_pool = upload_pool(solr, 0, doc_pool)

if __name__ == '__main__':
    main()

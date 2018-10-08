"""
Extract the features from the graphs and populate the feature
database
"""

import os
import sys
from fixrgraph.stat_sig.feat import (FeatExtractor, Feat)
from fixrgraph.stat_sig.db import FeatDb

def process_graph(graph_path, featDb):
    featExtractor = FeatExtractor(graph_path)

    graph_sig = featExtractor.get_graph_sig()
    featDb.insert_graph(graph_sig)

    for feat in featExtractor.get_features():
        featDb.insert_feat(graph_sig, feat)

def process_graphs(graph_path,
                   host,
                   user,
                   password,
                   db_name = "groum_features"):
    featDb = FeatDb(host, user, password, db_name)
    featDb.open()


    acdfgs = []
    for root, dirs, files in os.walk(graph_path, topdown=False):
        for name in files:
            if name.endswith("acdfg.bin"):
                filename = os.path.join(root, name)
                acdfgs.append(filename)

    i = 0
    for filename in acdfgs:
        i = i + 1
        print "Extracting %d/%d..." % (i, len(acdfgs))
        process_graph(filename, featDb)

    featDb.close()

def main():
    p = optparse.OptionParser()
    p.add_option('-g', '--graph_path', help="Path to the groum files")

    p.add_option('-a', '--host', help="Address to the db server")
    p.add_option('-u', '--user', help="User to access the db")
    p.add_option('-p', '--password', help="Password to the db")

    def usage(msg=""):
        if msg:
            print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)

    opts, args = p.parse_args()

    required = [opts.graph_path,opts.address,opts.user,opts.password]
    for r in required:
        if (not r):
            usage("Missing required argument!")
    if (not os.path.isdir(opts.graph_path)): usage("Path %s does not exists!" % opts.graph_path)



if __name__ == '__main__':
    main()

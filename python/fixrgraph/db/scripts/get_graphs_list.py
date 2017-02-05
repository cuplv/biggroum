""" Query the DB to get a list of the graphs to be used by the cluster computation

"""

import sys
import os
import optparse
import logging
import string
import collections

from fixrgraph.db.isodb import IsoDb

def main():
    logging.basicConfig(level=logging.DEBUG)

    p = optparse.OptionParser()
    p.add_option('-d', '--db', help="Database with data")
    p.add_option('-r', '--rel_path_graph', help="Relative path to the graph")
    p.add_option('-o', '--outfile', help="Output file for the list of isos")

    opts, args = p.parse_args()
    def usage(msg=""):
        if msg: print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)
    if (not opts.db or not os.path.isfile(opts.db)): usage("Missing db")
    if (not opts.rel_path_graph or not os.path.exists(opts.rel_path_graph)): usage("Missing relative file path: %s" % opts.rel_path_graph)
    if (not opts.outfile or os.path.isfile(opts.outfile)): usage("Out file not specified or already existing")

    # Load the isos from the DB
    db = IsoDb(opts.db)
    qres = db.get_relfile_graphs()
    count = 0
    outfile = open(opts.outfile, "w")
    for g in qres:
        outfile.write(opts.rel_path_graph)
        (graph_path,) = g
        outfile.write(graph_path)
        outfile.write("\n")
        count = count + 1
    outfile.close()
    print "Total %d" % count

if __name__ == '__main__':
    main()

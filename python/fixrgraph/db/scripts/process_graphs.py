# Builds the graph database

import sys
import os
import optparse
import logging
import string
import collections

from fixrgraph.db.isodb import IsoDb
import sqlalchemy

def main():
    logging.basicConfig(level=logging.DEBUG)

    p = optparse.OptionParser()
    p.add_option('-g', '--graph_dir', help="")
    p.add_option('-d', '--db', help="db path")
    def usage(msg=""):
        if msg: print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)
    opts, args = p.parse_args()

    if (not opts.db): usage("db not given")
    if (not opts.graph_dir): usage("no graph dirs")
    if (not os.path.isdir(opts.graph_dir)): usage("%s does not exist!" % opts.graph_dir)

    db = IsoDb(opts.db)

    for root, dirs, files in os.walk(opts.graph_dir):
        for name in files:
            if name.endswith(".acdfg.bin"):
                # insert the graph
                relpath = os.path.join(root.replace(opts.graph_dir, ""), name)
                name = name[:-len(".acdfg.bin")]
                try:
                    db.add_graph(name, relpath)
                except sqlalchemy.exc.IntegrityError as e:
                    logging.warn("Duplicate entry %s (%s)" % (name, relpath))

if __name__ == '__main__':
    main()

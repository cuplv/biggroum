""" Query the DB to get a list of isos filtered by weight.

"""

import sys
import os
import optparse
import logging
import string
import collections

from fixrgraph.db.isodb import IsoDb
from fixrgraph.scheduler.run_iso import Job

def main():
    logging.basicConfig(level=logging.DEBUG)

    p = optparse.OptionParser()
    p.add_option('-d', '--db', help="Database with data")
    p.add_option('-o', '--outfile', help="Output file for the list of isos")
    p.add_option('-w', '--min_weight', type="float",
                 help="minimum weight")
    opts, args = p.parse_args()
    def usage(msg=""):
        if msg: print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)
    if (not opts.db or not os.path.isfile(opts.db)): usage("Missing db")
    if (not opts.outfile or os.path.isfile(opts.outfile)): usage("Out file not specified or already existing")
    if ((not opts.min_weight)):
        usage("Min weight not specified or negative")

    # Load the isos from the DB
    db = IsoDb(opts.db)
    qres = db.get_isos_by_weight(opts.min_weight)
    count = 0
    outfile = open(opts.outfile, "w")
    for iso in qres:
        (_, isopath, _, _, _, _, _) = iso
        outfile.write("%s\n" % (isopath))
        count = count + 1
    outfile.close()
    print "Total %d" % count

    (mean, std) = db.get_weight_stats()
    print "Mean %f" % mean
    print "Standard deviation %f" % std

if __name__ == '__main__':
    main()



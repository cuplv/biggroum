# given a directory and an output directory, creates a tar file
# for each directory and then creates a tar file containing all the directories
#

import tarfile
import sys
import os
import optparse
import logging

req_version = (2,7)

def make_tar_for_dir(output_filename, source_dir):
    with tarfile.open(output_filename, "w") as tar:
        logging.info("Compressing %s to %s" % (source_dir, output_filename))
        tar.add(source_dir, arcname=os.path.basename(source_dir))
        tar.close()


def main():
    logging.basicConfig(level=logging.DEBUG)

    cur_version = sys.version_info
    if cur_version < req_version:
        logging.error("Your Python interpreter is too old. Please consider upgrading.")

        print "If you are on Janus you need to switch to Python 2.6:\n" \
            "Run the following commands\n" \
            "$> module load gcc/5.1.0\n" \
            "$> module load intel/15.0.2\n" \
            "$> module load python/2.7.10\n"

        sys.exit(1)


    p = optparse.OptionParser()
    p.add_option('-i', '--inputdir', help="input")
    p.add_option('-o', '--outputdir', help="outputdir")
    opts, args = p.parse_args()
    def usage(msg=""):
        if msg: print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)

    if (not opts.inputdir): usage("Missing input dir")
    if (not opts.outputdir): usage("Missing output dir")
    if (not os.path.isdir(opts.inputdir)): usage("%s directory does not exist" % opts.inputdir)
    if (not os.path.isdir(opts.outputdir)): usage("%s directory does not exist" % opts.outputdir)

    outputdir = opts.outputdir
    inputdir = opts.inputdir

    # create a tar of all the compressed dir
    dst_file = os.path.join(outputdir, os.path.basename(inputdir) + ".tar")
    make_tar_for_dir(dst_file, inputdir)


if __name__ == '__main__':
    main()

# given a directory and an output directory, creates a tar file
# for each directory and then creates a tar file containing all the directories
#

import tarfile
import sys
import os
import optparse
import logging

def make_tar_for_dir(output_filename, source_dir):
    with tarfile.open(output_filename, "w") as tar:
        logging.info("Compressing %s to %s" % (source_dir, output_filename))
        tar.add(source_dir, arcname=os.path.basename(source_dir))
        tar.close()


def main():
    logging.basicConfig(level=logging.DEBUG)
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
    if (os.path.isdir(opts.outputdir)): usage("%s directory *ALREADY* exists" % opts.outputdir)

    outputdir = opts.outputdir
    inputdir = opts.inputdir

    # Create output dir and tar
    tarname = os.path.join(outputdir, os.path.basename(outputdir) + ".tar")
    logging.info("Creating archive %s" % tarname)
    os.makedirs(outputdir)
    print tarname
    finaltar = tarfile.open(tarname, "w") # uncompressed tar

    # goes through all the directory in inputdir
    for f in os.listdir(inputdir):
        indir = os.path.join(inputdir, f)
        if (not os.path.isdir(indir)):
            logging.info("%s is not a directory %s" % indir)
            continue

        # create a tar of all the compressed dir
        dst_file = os.path.join(outputdir, f + ".tar")
        make_tar_for_dir(dst_file, indir)

        # add the tar
        finaltar.add(dst_file, os.path.join(os.path.basename(outputdir),
                                            os.path.basename(dst_file)))
        os.remove(dst_file)

        # deleting each tar once done
        # TODO

    finaltar.close()


if __name__ == '__main__':
    main()
                

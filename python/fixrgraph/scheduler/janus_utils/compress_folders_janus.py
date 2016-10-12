# Compress multiple folders distributing the load among different nodes

# given a directory and an output directory, creates a tar file
# for each directory and then creates a tar file containing all the directories
#

import tarfile
import sys
import os
import optparse
import logging
import string

# Template for the janus batch
janus_batch = \
"""#!/bin/bash
#SBATCH --job-name ${job_name}
#SBATCH --time 00:02:00
#SBATCH --nodes 1
#SBATCH --output ${job_out}
#SBATCH --mail-type=ALL
#SBATCH --mail-user=${mail_address}

date
echo "Start ${job_name}"

module load gcc/5.1.0
module load intel/15.0.2
module load python/2.7.10

# RUN THE SCRIPT

python ${python_run} -i ${inputdir} -o ${outputdir}

echo "End ${job_name}"
date"""

def _substitute(template, substitution):
    """Substitutes elements in template based on a given substitution.

    This method can be thought of as a shorthand for
    t = string.Template(template)
    return t.substitute(substitution)

    Args:
        template: A template.
        substitution: A substitution.

    Returns:
        The substituted template.
    """
    return string.Template(template).safe_substitute(substitution)



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
    os.makedirs(outputdir)

    # goes through all the directory in inputdir and creates the janus file to schedule
    # schedules them
    for f in os.listdir(inputdir):
        indir = os.path.join(inputdir, f)
        if (not os.path.isdir(indir)):
            logging.info("%s is not a directory" % indir)
            continue

        current_path = os.getcwd()
        slurm_file_path = os.path.join(current_path, f + ".bash")

        job_name = "copy_%s" % indir
        job_out_file_path = os.path.join(current_path, job_name + ".bash")
        job_out = os.path.join(current_path, f + ".out.txt")

        script_path = os.path.dirname(os.path.realpath(__file__))
        python_run = os.path.join(script_path,
                                  "compress_single_folder.py")
        if (not os.path.isfile(python_run)):
            logging.error("%s script not found!" % python_run)
            sys.exit(1)


        janus_param = {"job_name" : job_name,
                       "job_out" : job_out,
                       "mail_address" : "sergio.mover@colorado.edu",
                       "python_run" : python_run,
                       "inputdir" : indir,
                       "outputdir" : outputdir}

        slurm_script = _substitute(janus_batch, janus_param)
        logging.debug("Creating %s " % slurm_file_path)
        with open(slurm_file_path, 'w') as slurm_file:
            slurm_file.write(slurm_script)
            slurm_file.close()

        # schedule the file
        logging.info("Scheduling %s " % slurm_file_path)
        os.system('sbatch %s' % slurm_file_path)
        os.remove(slurm_file_path)

if __name__ == '__main__':
    main()

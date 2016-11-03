""" Scheduler of the isomorphisms for a local machine and Janus

Creates a list of jobs for janus (SLURM script) or a local machine (make script)

"""

import sys
import os
import optparse
import logging
import json # for reading the traces from file
import string


# Template for the janus batch
janus_batch = \
"""#!/bin/bash
#SBATCH --job-name ${job_name}
#SBATCH --time 00:00:${to_sec}
#SBATCH --nodes 1
#SBATCH --output ${job_out}
#SBATCH --mail-type=ALL
#SBATCH --mail-user=${mail_address}

date
echo "Start ${job_name}"

# RUN THE SCRIPT

python ${python_run} -i '${iso_bin}' -j '${sched_list}' -s '${SLURM_SCRATCH}' -t ${single_to}

echo "End ${job_name}"
date
"""

# Template for the script invoked by make
# We keep the SBATCH comments in the make scheduler, we use
# them as meta-information in the log extraction script
make_batch = \
"""#!/bin/bash
#SBATCH --job-name ${job_name}
#SBATCH --time 00:00:${to_sec}
#SBATCH --nodes 1
#SBATCH --output ${job_out}
#SBATCH --mail-type=ALL
#SBATCH --mail-user=${mail_address}

date
echo "Start ${job_name}"

# RUN THE SCRIPT
ulimit -t ${to_sec}; python ${python_run} -i '${iso_bin}' -j '${sched_list}' -s '${SLURM_SCRATCH}' -t ${single_to} &> '${job_out}'

echo "End ${job_name}"
date
"""


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

class SchedulerType():
    JANUS, MAKE = range(2)

class JobCreator():
    """ Class used to create the jobs."""

    def __init__(self, index_file_name, graph_dir, old_graphs_prefix,
                 job_size, job_dir, iso_dir,
                 iso_binary, python_script, scratch_dir,
                 time_out, scheduler_type):
        """ The input parameters are:
        - index_file_name: the file containing the index of isomorphisms
        - graph_dir: path to the directory containing the graphs
          accessible by the machine that runs the jobs
        - old_graphs_prefix: to the directory containing the graphs
          used in the index file
        - job_size: number of isomorphisms computed per job
        - job_dir: output directory for the jobs
        - iso_dir: output directory of the isomorphisms (accessible
          from the target machine)
        - iso_binary: binary of the isomorphism checker (also accessible...)
        - python_script: script to invoke to compute the jobs (usually
          run_iso.py, need the path accessible from the target machine)
        - scratch_dir: temporary directory on the target machine
        - time_out: time out to compute one single isomorphisms.
        """

        self.index_file_name = index_file_name
        self.graph_dir = graph_dir
        self.old_graphs_prefix = old_graphs_prefix

        self.job_size = job_size
        self.job_dir = job_dir
        self.iso_dir = iso_dir

        self.iso_binary = iso_binary
        self.python_script =  python_script
        self.scratch_dir = scratch_dir

        self.time_out = time_out
        self.scheduler_type = scheduler_type

    def createJobs(self):
        """ Creates the list of jobs in self.job_dir."""
        logging.info("Create jobs...")
        logging.info("Job size %d" % self.job_size)
        job_index = self._get_job_index()

        logging.info("Reading index file...")
        with open(self.index_file_name, 'r') as index_file:
            index_data = json.load(index_file)

        counter = 0
        job_list = []
        target_id = -1
        logging.info("Processing isos...")
        # Collect the list of isomorphism to compute and create a job
        # as soon as there are enough isomorphisms (i.e.
        # self.job_size)
        #
        # Concurrently, write the main script to scheduler/run all the jobs
        for pair in index_data:
            assert len(pair) == 2
            counter = counter + 1
            graph1_name = pair[0]
            graph2_name = pair[1]

            # We require that the index builds pairs of graphs that are ordered
            # lexicographically
            # This is a useful default for finiding an isomorphism from its
            # composing graphs.
            assert graph1_name <= graph2_name

            # replace the old graph path with the new one
            if (self.old_graphs_prefix is not None):
                graph1_name = graph1_name.replace(self.old_graphs_prefix, self.graph_dir)
                graph2_name = graph2_name.replace(self.old_graphs_prefix, self.graph_dir)

                if (not os.path.isfile(graph1_name)):
                    raise Exception("%s graph file not found!" % graph1_name)
                if (not os.path.isfile(graph2_name)):
                    raise Exception("%s graph file not found!" % graph2_name)

            job_list.append((graph1_name, graph2_name))

            if (counter > self.job_size):
                logging.info("Creating job...")
                # Write a single job
                target_id = self._write_jobs(job_index, job_list, target_id)
                counter = 0
                job_list = []

        if counter > 0:
            # write leftovers
            logging.info("Creating job...")
            target_id = self._write_jobs(job_index, job_list, target_id)

        self._job_index_close(job_index, target_id)


    @staticmethod
    def _join_path(path_list):
        if len(path_list) == 1:
            a=path_list[0]
            return a.encode('ascii','ignore')
        else:
            res = JobCreator._join_path(path_list[1:])
            return os.path.join(path_list[0], res)


    def get_script(self, folders, job_name, abs_job_path,
                   overall_to):
        # wirte the SLURM bash file for janus
        rel_slurm_path = JobCreator._join_path(folders + [job_name + ".bash"])
        abs_slurm_path = JobCreator._join_path([self.job_dir] + [rel_slurm_path])
        rel_out_path  = JobCreator._join_path(folders + [job_name + ".out"])
        abs_out_path  = JobCreator._join_path([self.job_dir] + [rel_out_path])

        subs_map = {"iso_bin" : self.iso_binary,
                    "job_name" : job_name,
                    "job_out" : abs_out_path,
                    "mail_address" : "sergio.mover@colorado.edu",
                    "python_run" : self.python_script,
                    "sched_list" : abs_job_path,
                    "single_to" : str(self.time_out),
                    "to_sec" : str(overall_to),
                    "SLURM_SCRATCH" : self.scratch_dir}

        if (self.scratch_dir is not None):
            subs_map["scratch_path"] = self.scratch_dir

        if (self.scheduler_type == SchedulerType.JANUS):
            template = janus_batch
        elif (self.scheduler_type == SchedulerType.MAKE):
            template = make_batch
        else:
            raise Exception("Unknown scheduler type")

        slurm_script = _substitute(template, subs_map)
        return (rel_slurm_path, abs_slurm_path, slurm_script)


    def _write_jobs(self, job_index, job_list, target_id):
        """ Write a single job
        It also update the main script used to schedule/run the jobs
        """
        def _get_path(acdfg_name):
            splitted = acdfg_name.split(".")
            return splitted

        assert len(job_list) >= 1
        repr_iso = job_list[0]
        assert len(repr_iso) == 2

        repr1_name = os.path.basename(repr_iso[0]).replace(".acdfg.bin", "")
        repr2_name = os.path.basename(repr_iso[1]).replace(".acdfg.bin", "")
        job_name = repr1_name + "_job_" + repr2_name

        repr1_list = _get_path(repr1_name)
        repr2_list = _get_path(repr2_name)
        folders = repr1_list + repr2_list

        abs_dir = JobCreator._join_path([self.job_dir] + folders)
        if (not os.path.isdir(abs_dir)): os.makedirs(abs_dir)

        rel_job_path = JobCreator._join_path(folders + [job_name + ".txt"])
        abs_job_path = JobCreator._join_path([self.job_dir] + [rel_job_path])

        with open(abs_job_path, 'w') as job_file:
            # Write the graphs directory and the
            # output directory to be used by each Janus node
            # to get the data and store the input
            #
            # WARNING: they must be accessible by the nodes
            job_file.write("%s\n" % self.graph_dir)
            job_file.write("%s\n" % self.iso_dir)
            for p in job_list:
                job_file.write("%s %s\n" % (p[0], p[1]))
            job_file.flush()
            job_file.close()

        # write the script that execute a single job
        overall_to = (self.time_out + 1) * self.job_size
        (rel_slurm_path, abs_slurm_path, slurm_script) = self.get_script(folders, job_name, abs_job_path, overall_to)

        with open(abs_slurm_path, 'w') as slurm_file:
            slurm_file.write(slurm_script)
            slurm_file.close()

        # build the index with the relative file path
        if (self.scheduler_type == SchedulerType.JANUS):
            self._job_index_append(job_index, "sbatch '%s'" % rel_slurm_path)
        elif (self.scheduler_type == SchedulerType.MAKE):
            target_id = target_id + 1
            target_name = "target_%d" % target_id
            escaped = rel_slurm_path.replace("$","$$")
            self._job_index_append(job_index, "%s:\n\tbash '%s'\n\n" % (target_name, escaped))
        else:
            raise Exception("Unknown scheduler type")

        return target_id


    def _get_job_index(self):
        """ get the job index file"""
        fname = os.path.splitext(os.path.basename(self.index_file_name))[0]

        if (self.scheduler_type == SchedulerType.JANUS):
            filename = "scheduler_%s.bash" % fname
        elif (self.scheduler_type == SchedulerType.MAKE):
            filename = "scheduler_%s.make" % fname
        else:
            raise Exception("Unknown scheduler type")

        job_index_path = os.path.join(self.job_dir, filename)

        append = False
        if (os.path.isfile(job_index_path)):
            logging.warning("Appending to existing file %s" % job_index_path)
            append = True

        job_index_file = open(job_index_path, 'w+')
        if not append:
            self._job_index_append(job_index_file, "#!/bin/bash")

            if (SchedulerType.MAKE == self.scheduler_type):
                self._job_index_append(job_index_file, "MAIN: ALL\n\t\n")

        return job_index_file

    def _job_index_append(self, job_index, rel_job_path):
        job_index.write("%s\n" % rel_job_path)

    def _job_index_close(self, job_index, target_id):
        logging.info("Written job_index...")

        # add target with all the subtargets
        if (SchedulerType.MAKE == self.scheduler_type):
            all_targets = ["target_%d" % l for l in range(target_id+1)]
            target_string = " ".join(all_targets)
            job_index.write("ALL: %s\n\t\n" % (target_string))
            job_index.flush()

        job_index.close()


def main():
    logging.basicConfig(level=logging.DEBUG)

    #
    p = optparse.OptionParser()
    p.add_option('-i', '--index', help="Json index file")
    p.add_option('-g', '--graphs', help="Input graph directory")
    p.add_option('-n', '--old_graphs_prefix', help="Prefix to graph path in the index")
    p.add_option('-j', '--jobdir', help="Output job directory")
    p.add_option('-o', '--iso', help="Output isomorphism directory")
    p.add_option('-s', '--job_size', default=5,
                 help="Number of isomorphism in one partition")

    p.add_option('-b', '--iso_binary', help="Path to the isomorphism binary")
    p.add_option('-p', '--python_script', help="Path to the python run script")
    p.add_option('-t', '--timeout', type="int", help="max timeout for a single iso check")
    p.add_option('-l', '--scratch', help="Path to the scratch folder")

    p.add_option('-m', '--scheduler', type='choice',
                 choices= ["make","janus"],
                 help="Scheduler type (local with make or janus)",
                 default = "make")

    p.add_option('-f', '--force', action="store_true",
                 default=False, help="Does not complain if dir exists")

    def usage(msg=""):
        if msg: print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)

    opts, args = p.parse_args()

    if (opts.scheduler == "make"):
        scheduler_type = SchedulerType.MAKE
    elif (opts.scheduler == "janus"):
        scheduler_type = SchedulerType.JANUS
    else:
        raise Exception("Unkown scheduler type %s" % opts.scheduler)

    # Check for files
    must_exists_file = [("Index file", opts.index),
                        ("Isomorphism binary", opts.iso_binary),
                        ("Python script", opts.python_script)]
    for (d,f) in must_exists_file:
        if (not f): usage("%s not provided" % d)
        if (not os.path.isfile(f)):
            usage("%s (%s) file does not exists" % (f,d))

    # check for dirs
    must_exists_dir = [("Graphs dir", opts.graphs, True),
                       ("Job dirs", opts.jobdir, False),
                       ("Isomorphisms dirs", opts.iso, False)]
    for (d,f,must_exist) in must_exists_dir:
        if (not f): usage("%s not provided" % d)

        if (must_exist and not os.path.isdir(f)):
            usage("%s (%s) directory does not exists" % (f,d))

        if ( (not must_exist) and (not opts.force) and os.path.isdir(f)):
            usage("%s (%s) directory ALREADY not exists" % (f,d))
    if opts.scratch:
        if (not os.path.isdir(opts.scratch)):
            usage("%s (scratch) directory does not exists" % (os.path.isdir))
    else:
        usage("Scratch directory not specified!")


    try:
        job_size = int(opts.job_size)
        if (job_size < 1):
            usage("The number of isomorphism checks in a partition must be positive")
    except Exception as e:
        usage("Job size is not a number")

    if (opts.timeout < 0): usage("Timeout cannot be negative")

    # Create scheduler and output dir
    if (not os.path.isdir(opts.jobdir)): os.makedirs(opts.jobdir)
    if (not os.path.isdir(opts.iso)): os.makedirs(opts.iso)

    # Create jobs
    jobCreator = JobCreator(opts.index, opts.graphs, opts.old_graphs_prefix,
                            job_size, opts.jobdir, opts.iso,
                            opts.iso_binary, opts.python_script, opts.scratch,
                            opts.timeout, scheduler_type)
    jobCreator.createJobs()


    # Schedule jobs

if __name__ == '__main__':
    main()

"""
Script that invokes the isomorphism checker on a batch of jobs (either
using SLURM or make).
"""

import os
import stat
import sys
import optparse
import logging
import shutil
import subprocess
from threading import Timer

class Job:
    def __init__(self, job_file):
        self.graph_folder = None
        self.out_folder = None
        self.iso_checks = []

        self._read_job_file(job_file)

    def get_graph_path(self, graph_name):
        graph_path = os.path.join(self.graph_folder,
                                  graph_name)
        return graph_path

    @staticmethod
    def get_dst_iso_path(out_folder, g1_base, g2_base):
        if (g1_base < g2_base): gname = g1_base
        else: gname = g2_base

        gname_list = gname.replace(".acdfg.bin","").split(".")
        path = ""
        for l in os.path.join(gname_list): path = os.path.join(path,l)
        graph_path = os.path.join(out_folder, path)

        if (not os.path.isdir(graph_path)):
            os.makedirs(graph_path)

        return graph_path

    def _read_job_file(self, job_file):
        READ_GRAPH = 0
        READ_FOLDER = 1
        READ_ISO = 2

        logging.debug("Reading job file...")

        status = READ_GRAPH
        for line in job_file.readlines():
            line = line.strip()
            line = line.replace("\n","")
            if (status == READ_GRAPH):
                self.graph_folder = line
                logging.debug("Graph path is %s" % self.graph_folder)
                status = status + 1 # read folder
            elif (status == READ_FOLDER):
                self.out_folder = line
                logging.debug("Out path is %s" % self.out_folder)
                status = status + 1 # read isos
            else:
                assert status == READ_ISO
                pair = line.split(" ")
                assert len(pair) == 2
                self.iso_checks.append(pair)


def copy_to(fileToCopy, dstPath):
    filename = os.path.os.path.basename(fileToCopy)
    dst_name = os.path.join(dstPath, filename)
    shutil.copyfile(fileToCopy, dst_name)
    assert (os.path.isfile(dst_name))
    return dst_name


def _get_subproc_times(time_tuple):
    # user time, system time, children user time, children system time,
    # and elapsed real time since a fixed point in the past

    return (time_tuple[2], time_tuple[3])


def _diff_times(tuple1, tuple2):
    diff_list = []
    assert (len(tuple1) == len(tuple2))
    for (t1,t2) in zip(tuple1, tuple2):
        diff_list.append(t1 - t2)
    return diff_list

def _write_times(stream, time_tuple):
    stream.write("User: %f\n" % time_tuple[0])
    stream.write("System: %f\n" % time_tuple[1])
    stream.flush()


def main():
    logging.basicConfig(format='%(asctime)s =  %(message)s', level=logging.DEBUG)
    logging.info("run_iso.py: start the execution")

    p = optparse.OptionParser()
    p.add_option('-i', '--iso', help="Path to the isomorphism binary")
    p.add_option('-j', '--job', help="Path to the job file")
    p.add_option('-s', '--scratch', help="Path to the scratch folder")
    p.add_option('-t', '--timeout', type="int", help="max timeout for the iso check")

    def usage(msg=""):
        if msg:
            logging.error("Usage error: %s " % msg)
            print "----\n%s\n----\n" % msg
        else:
            logging.error("Usage error")
        p.print_help()
        sys.exit(1)
    opts, args = p.parse_args()

    must_exists_file = [("Isomorphism binary", opts.iso),
                        ("Job file", opts.job)]
    must_exists_path = [("Scrat path", opts.scratch)]
    for (d,f) in must_exists_file:
        if (not f): usage("%s not provided" % d)
        if (not os.path.isfile(f)):
            usage("%s (%s) file does not exists" % (f,d))
    for (d,f) in must_exists_path:
        if (not f): usage("%s not provided" % d)
        if (not os.path.isdir(f)):
            usage("%s (%s) directory does not exists" % (f,d))
    if (not opts.timeout): usage("Timeout not provided!")
    if (opts.timeout < 0): usage("Timeout cannot be negative!")

    # 0. Read the job file
    logging.info("Reading the job file %s" % opts.job)
    job_file = open(opts.job, 'r')
    job = Job(job_file)
    job_file.close()

    # scratch folder for the job
    job_name = os.path.splitext(os.path.basename(opts.job))[0]
    scratch_path = os.path.join(opts.scratch, job_name)
    logging.info("Creating scratch folder in %s" % scratch_path)
    if (not os.path.isdir(scratch_path)): os.makedirs(scratch_path)

    # 1. Copy data to scratch
    logging.info("Copying files...")
    # Copy the iso binary
    iso_bin_path = copy_to(opts.iso, scratch_path)
    st = os.stat(iso_bin_path) # make it executable
    os.chmod(iso_bin_path, st.st_mode | stat.S_IEXEC)

    # Copy the set of graphs used in the iso checks
    graphs_to_copy = set([])
    for check in job.iso_checks:
        assert len(check) == 2
        graphs_to_copy.add(check[0])
        graphs_to_copy.add(check[1])
    for graph in graphs_to_copy:
        source_path = job.get_graph_path(graph)
        copy_to(source_path, scratch_path)

    # 2. For each pair, run the isomorphism (bounded in time)
    iso_files = []
    log_files = []
    for check in job.iso_checks:
        assert len(check) == 2
        graph_1 = check[0]
        graph_2 = check[1]

        graph_1_file = job.get_graph_path(graph_1)
        graph_2_file = job.get_graph_path(graph_2)
        graph_1_base = os.path.basename(graph_1_file).replace(".acdfg.bin","")
        graph_2_base = os.path.basename(graph_2_file).replace(".acdfg.bin","")

        # iso_name - name_acdfg_1_name_acfg_2
        iso_prefix = "%s_%s" % (graph_1_base, graph_2_base)
        iso_file_prefix = os.path.join(scratch_path, "%s" % iso_prefix)
        iso_file = "%s.iso.bin" % iso_file_prefix
        iso_dot_file = "%s.dot" % iso_file_prefix
        stdout_file = os.path.join(scratch_path, "%s.stdout" % iso_prefix)
        stderr_file = os.path.join(scratch_path, "%s.stderr" % iso_prefix)


        try:
            out = open(stdout_file,"wb")
            err = open(stderr_file,"wb")

            logging.info("Running the isomorphism check on %s %s (result in %s)" % (graph_1_file, graph_2_file, iso_file_prefix))

            args = [iso_bin_path, graph_1_file, graph_2_file, iso_file_prefix]
            logging.debug("Command line %s" % " ".join(args))
            proc = subprocess.Popen(args, stdout=out, stderr=err, cwd=None)

            # Kill the process after the timout expired
            def kill_function(p, g1, g2):
                logging.info("Execution timed out for: %s %s" % (g1,g2))
                out.flush()
                err.flush()

                p.kill()

                # write the log
                err.write("Execution timed out")
                after_subproc_times = _get_subproc_times(os.times())
                subproc_time = _diff_times(after_subproc_times, before_subroc_times)
                logging.info("Exec time %f %f " % (after_subproc_times[0], before_subroc_times[1]))
                _write_times(err, subproc_time)

                out.flush()
                err.flush()

            before_subroc_times = _get_subproc_times(os.times())

            timer = Timer(opts.timeout, kill_function, [proc, graph_1_file, graph_2_file])
            try:
                timer.start()

                # execute the process
                proc.wait()
                after_subproc_times = _get_subproc_times(os.times())

            except Exception as e:
                logging.error(e.message)

            finally:
                # Cancel the timer, no matter what
                timer.cancel()
                out.flush()
                err.flush()

            return_code = proc.returncode

            if (return_code != 0):
                err_msg = "Error code is %s\nCommand line is: %s\n%s" % (str(return_code), str(" ".join(args)),"\n")
                logging.error("Error executing %s\n%s" % (" ".join(args), err_msg))
            else:
                logging.info("Computed isomorphism for %s %s (result in %s)" % (graph_1_file, graph_2_file, iso_file_prefix))
                subproc_time = _diff_times(after_subproc_times, before_subroc_times)
                logging.info("Exec time %f %f " % (subproc_time[0], subproc_time[1]))
                _write_times(err, subproc_time)

                dst_iso_path = Job.get_dst_iso_path(job.out_folder,
                                                    graph_1_base, graph_2_base)
                dst_dot_path = Job.get_dst_iso_path(job.out_folder,
                                                    graph_1_base, graph_2_base)

                iso_files.append((iso_file, dst_iso_path))
                iso_files.append((iso_dot_file, dst_dot_path))

            out.close()
            err.close()
        except Exception as e:
           logging.error(e.message)

        if (os.path.isfile(stderr_file)):
            log_files.append(stderr_file)
        if (os.path.isfile(stdout_file)):
            log_files.append(stdout_file)


    # 3. Copy the data from scratch back to the server
    logging.info("Copying the isomorphism results...")
    for (iso_name, dst_iso_path) in iso_files:
        if (not os.path.isfile(iso_name)):
            logging.warning("Skipping results %s" % iso_name)
        else:
            logging.info("Copying %s" % iso_name)
            copy_to(iso_name, dst_iso_path)

    logging.info("Copying the execution logs...")
    job_dir = os.path.dirname(opts.job)
    for log_file in log_files:
        if (not os.path.isfile(log_file)):
            logging.warning("Skipping log %s" % log_file)
        else:
            logging.info("Copying log %s" % log_file)
            copy_to(log_file,job_dir)

    # 4. Delete data from scratch (not necessary in Janus)
    logging.info("Cleaning scratch...")
    # shutil.rmtree(scratch_path)

    logging.info("Done")

if __name__ == '__main__':
    main()


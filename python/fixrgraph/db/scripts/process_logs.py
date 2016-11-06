""" Process the logs produced by the scheduler

Input:
  - scheduling file produced by the scheduler
  - directory that contains the jobs
  - old absolute directory of the job folder (to enable rebasing of the paths)

Output:
  - Database containing:
    - Paths to graphs
    - Isomorphism relations
    - Table of statistics for the computation
      The statistics collected are:
        - status of the computation: ok|to|error
        - result of the isomorphism check: iso|noniso|unknow
        - time took to compute it (or to if time out)
        - weight of the isomorhism

In the future, the database should be updated directly by the script that executes
the isomorhism checks (run_iso.py)
"""

import sys
import os
import optparse
import logging
import string
import collections

from fixrgraph.db.isodb import IsoDb
from fixrgraph.scheduler.run_iso import Job

import sqlalchemy


MAX_RECORD = 10000
IsoData = collections.namedtuple("IsoData",
                                 ["graph1", "graph2",
                                  "status", "runtime",
                                  "isores", "weight",
                                  "isoname"],
                                 verbose=False,
                                 rename=False)


def find_out_file(bash_script_path):
    """ Find the output file in the log.

    An example of output file path is:
    #SBATCH --output /lustre/janus_scratch/semo2007/jobs/microsoft/aspnet/signalr/client/test/integration/android/MainActivity_onOptionsItemSelected/com/mendeley/example/ExampleActivity_onOptionsItemSelected/microsoft.aspnet.signalr.client.test.integration.android.MainActivity_onOptionsItemSelected_job_com.mendeley.example.ExampleActivity_onOptionsItemSelected.out
    """

    script_file = open(bash_script_path, 'r')
    for line in script_file:
        line = line.strip()
        if not line.startswith("#SBATCH --output"): continue
        out_file_path = line[len("#SBATCH --output"):].strip()

        return out_file_path
    return None

def get_graph_info(old_graph_dir, graph_path):
    if graph_path.startswith(old_graph_dir):
        graph_path = graph_path.replace(old_graph_dir, "")

    graph_name = os.path.basename(graph_path).replace(".acdfg.bin" ,"")
    return (os.path.dirname(graph_path), graph_name)


def get_graphs_names(old_graph_dir, log_line):
    splitted = log_line.split(" ")
    assert len(splitted) >= 2

    (p1, s1) = get_graph_info(old_graph_dir, splitted[0])
    (p2, s2) = get_graph_info(old_graph_dir, splitted[1])
    return (s1, s2)

class ProcessLog(object):
    def __init__(self, db, old_graph_dir):
        self.db = db
        self.old_graph_dir = old_graph_dir

        self.graphidmap = {}
        self.iso_list = []

    def get_graphid(self, graphname):
        if graphname in self.graphidmap:
            return self.graphidmap[graphname]
        else:
            gid = self.db.get_graph_id(graphname)
            self.graphidmap[graphname] = gid
            return gid

    def _write_list(self, iso_list):
        print "Writing list of %d" % len(iso_list)

        rec_list = []
        log_list = []
        for d in iso_list:
            g1id = self.get_graphid(d.graph1)
            g2id = self.get_graphid(d.graph2)
            iso_prefix = "%s_%s" % (d.graph1, d.graph2)
            isopath = Job.get_dst_iso_path("", d.graph1, d.graph2, False)
            isopath = os.path.join(isopath, iso_prefix + ".iso.bin")

            try:
                weight = float(d.weight)
            except Exception as e:
                weight = -1

            rec_list.append((g1id, g2id, d.isoname, isopath, weight))
            log_list.append((d.isoname, d.status, d.runtime, 0, d.isores))

        try:
            print "Adding list of isomorphisms..."
            self.db.add_iso(rec_list)
            print "Adding logs"
            self.db.add_log(log_list)
        except sqlalchemy.exc.IntegrityError as e:
            logging.warn("Duplicate entry %s" % d.isoname)
        except Exception as e:
            logging.error("Error inserting data...")

    def _add_data(self, iso_list, isoData):
        iso_list.append(isoData)
        if (len(iso_list) > MAX_RECORD):
            self._write_list(iso_list)
            return []
        else:
            return iso_list


    def process_job_out(self, job_output_log):
        """ Process the output file of the job.
        We write the file directly since the log can be huge.

        From the log we get the list of isomorphisms.
        Each isomorphism has:
        - pair of involved ACDFGs
        - status
        - runtime
        - result of the iso
        - weight of the iso
        """

        # Strings to match
        RUNNING_ISO="Running the isomorphism check on "
        COMPUTED_ISO="Computed isomorphism for "
        EXEC_TIME_STR="Exec time "
        EXEC_TO="Execution timed out for: "
        EXEC_ERROR="Error executing "


        # states of the log
        START = 0
        RUNNING = 1
        COMPUTED = 2
        EXEC_TIME = 3
        TO = 4
        DONE = 5

        def _get_log_data(line):
            splitted = line.split("=")
            if len(splitted) > 1:
                app = ("=".join(splitted[1:])).strip()
                return app.strip()
            else:
                return None

        def get_iso_name(log_data):
            splitted = line.split("result in ")
            if (len(splitted) > 1):
                app = splitted[1]
                if (app[len(app) - 1] == ")"): app = app[:-1]
                app = os.path.basename(app)
                return app
            else:
                return None

        def get_user_time_file(stderr):
            (user,sys) = ("?", "?")
            with open(stderr, 'r') as f:
                for l in f:
                    l = l.strip()
                    if l.startswith('User: '):
                        (user,sys) = (l.replace('User: ',''), sys)
                    elif l.startswith('System: '):
                        (user,sys) = (user, l.replace('System: ',''))
            return (user,sys)

        def get_res(stdout):
            (res,weight) = ("noniso", "?")
            with open(stdout, 'r') as f:
                for l in f:
                    l = l.strip()
                    if l.startswith('Problem sucessfully solved !'):
                        (res, weight) = ("iso", weight)
                    elif l.startswith('Objective Value : '):
                        (res, weight) = (res, l.split(" : ")[1])
            return (res, weight)

        def reset(self_instance, inst_data=None, proper=True):

            # Insert the isomorphism result as error, if there are
            # enough information
            if (inst_data is not None):
                if (inst_data[0]is not None and
                    inst_data[1] is not None and
                    inst_data[6] is not None):

                    isoData = IsoData(inst_data[0], inst_data[1],
                                      "error", "?", "?", "?",
                                      inst_data[6])
                    self.iso_list = self._add_data(self.iso_list, isoData)

            state = START
            inst_data = [None, None, "?", "?", "?", "?", None]
            if (not proper): logging.warning("resetting")
            return (state, inst_data, None, None)

        # states
        # 0: start
        # 1: running
        # 2: computed
        # 3: exec time
        # 4: exec to
        # 5: exec time
        state = START
        inst_data = [None, None, "?", "?", "?", "?", None]

        # A well formed log for a single isomorphisms should contain,
        # in this order, the lines:
        #
        # Running the isomorphism check on ...
        # Computed isomorphism for...
        # Exec time...
        #
        # or
        #
        # Running the isomorphism check on ...
        # Computed isomorphism for...
        # Execution timed out for...
        #
        # or
        # Running the isomorphism check on ...
        # Computed isomorphism for...
        # Error executing
        #
        # We process the log file one by one, matching these three
        # patterns
        #

        logging.info("Processing %s..." % job_output_log)
        jobout_file = open(job_output_log, 'r')

        # old, bad state iteration
        linenum = -1
        for line in jobout_file.readlines():
            linenum = linenum + 1
            if not line: continue
            line = line.strip()

            log_data = _get_log_data(line)
            if None == log_data: continue

            # Here we have a log, check its kind

            if (log_data.startswith(RUNNING_ISO)):
                # See the run iso message once
                log_data = log_data[len(RUNNING_ISO):]

                # RESET
                if state != 0:
                    (state, inst_data, stdout, stderr) = reset(self, inst_data, False)

                (g1,g2) = get_graphs_names(self.old_graph_dir, log_data)
                iso_name = get_iso_name(log_data)
                inst_data[6] = iso_name
                inst_data[0] = g1
                inst_data[1] = g2
                state = RUNNING
            elif (log_data.startswith(COMPUTED_ISO)):
                log_data = log_data[len(COMPUTED_ISO):]

                if state != 1:
                    # RESET - some step was missing...
                    (state, inst_data, stdout, stderr) = reset(self, inst_data, False)
                    continue

                (a,b) = get_graphs_names(self.old_graph_dir, log_data)

                if (g1,g2) != (a,b):
                    # RESET - some step was missing...
                    (state, inst_data, stdout, stderr) = reset(self, inst_data, False)
                    continue

                inst_data[2] = "ok"
                state = COMPUTED
            elif (log_data.startswith(EXEC_TIME_STR)):
                log_data = log_data[len(EXEC_TIME_STR):]

                if inst_data[6] is None or inst_data[0] is None or inst_data[1] is None:
                    # did not really
                    (state, inst_data, stdout, stderr) = reset(self, inst_data, False)
                    continue

                stdout = inst_data[6] + ".stdout"
                stderr = inst_data[6] + ".stderr"
                if state == COMPUTED:
                    if not (stdout is not None and stderr is not None):
                        # RESET - some step was missing...
                        (state, inst_data, stdout, stderr) = reset(self, inst_data, False)
                        continue

                    stdout = os.path.join(os.path.dirname(job_output_log),
                                          stdout)
                    stderr = os.path.join(os.path.dirname(job_output_log),
                                          stderr)

                    if (not os.path.isfile(stderr)):
                        logging.error("Cannot read error log %s" % (stderr))
                        (state, inst_data, stdout, stderr) = reset(self, inst_data, False)
                        continue
                    else:
                        (user_time, sys_time) = get_user_time_file(stderr)
                        inst_data[3] = user_time

                    if (not os.path.isfile(stdout)):
                        logging.error("Cannot read error log %s" % (stdout))
                        (state, inst_data, stdout, stderr) = reset(self, inst_data, False)
                        continue
                    else:
                        (res, weight) = get_res(stdout)
                        inst_data[4] = res
                        inst_data[5] = weight

                    isoData = IsoData(inst_data[0], inst_data[1],
                                      inst_data[2], inst_data[3],
                                      inst_data[4], inst_data[5],
                                      inst_data[6])
                    self.iso_list = self._add_data(self.iso_list, isoData)
                    (stdout, stderr) = (None, None)

                    (state, inst_data, stdout, stderr) = reset(self, None)

                elif state == EXEC_TIME:
                    state == DONE
                else:
                    # RESET - some step was missing...
                    (state, inst_data, stdout, stderr) = reset(self, inst_data, False)
                    continue

            elif (log_data.startswith(EXEC_TO)):
                log_data = log_data[len(EXEC_TO):]
                if state != 1:
                    (state, inst_data, stdout, stderr) = reset(self, inst_data, False)
                    continue

                inst_data[2] = "to"
                inst_data[3] = "?"
                inst_data[5] = "?"
                state = EXEC_TIME
            elif (log_data.startswith(EXEC_ERROR)):
                # Error goes back to start
                # Store instance
                log_data = log_data[len(EXEC_ERROR):]

                if (state > 1):
                    inst_data[2] = "error"
                    isoData = IsoData(inst_data[0], inst_data[1],
                                      inst_data[2], inst_data[3],
                                      inst_data[4], "?",
                                      inst_data[6])
                    self.iso_list = self._add_data(self.iso_list, isoData)
                    (state, inst_data, stdout, stderr) = reset(self, None)
                else:
                    (state, inst_data, stdout, stderr) = reset(self, inst_data, False)

def main():
    logging.basicConfig(level=logging.DEBUG)

    p = optparse.OptionParser()
    p.add_option('-s', '--sched_file', help="Scheduling script")
    p.add_option('-j', '--job_dir', help="Directory containing the job information")
    p.add_option('-n', '--old_job_dir', help="Path of the job dir (used in the actual logs)")
    p.add_option('-g', '--old_graph_dir', help="Path of the old graph dir")
    p.add_option('-o', '--out_db', help="Name of the output db")
    def usage(msg=""):
        if msg: print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)
    opts, args = p.parse_args()

    if (not opts.sched_file): usage("Scheduler file not given")
    if (not opts.job_dir): usage("Job directory not given")
    if (not opts.out_db): usage("Database to store data")
    if (not os.path.isfile(opts.sched_file)): usage("%s does not exist!" % opts.sched_file)
    if (not os.path.isdir(opts.job_dir)): usage("%s does not exist" % opts.job_dir)

    if (not opts.old_job_dir): usage("Old job directory missing")
    if (not opts.old_graph_dir): usage("Old graph dir missing")

    sched_file_name = opts.sched_file
    job_dir = opts.job_dir
    old_job_dir = opts.old_job_dir
    old_graph_dir = opts.old_graph_dir

    db = IsoDb(opts.out_db)

    sched_file = open(sched_file_name, 'r')
    totlines=0
    for line in sched_file.readlines():
        totlines=totlines+1
    sched_file.close()

    # Open the scheduler file and visit it
    sched_file = open(sched_file_name, 'r')
    i = 0
    pl = None
    for line in sched_file.readlines():
        i = i + 1
        logging.info("Processing %d/%d" % (i, totlines))
        line = line.strip()
        if not (line.startswith("sbatch ") or line.startswith("bash ")):
            continue

        is_make = False
        if line.startswith("sbatch "):
            line = line.replace("sbatch ", "")
            line = line.replace("'", "").strip()
        if line.startswith("bash "):
            is_make = True
            line = line.replace("bash ", "")
            line = line.replace("'", "").strip()

        # get the bash script
        bash_script_path = os.path.join(job_dir, line)
        if (is_make):
            # fix the weird escaping of make
            bash_script_path = bash_script_path.replace("$$","$")

        if (not os.path.isfile(bash_script_path)):
            logging.error("Scheduler script %s not " \
                          "found! skipping it" % bash_script_path)
            continue

        out_file_path = find_out_file(bash_script_path)
        # fix the absolute path
        if (out_file_path.startswith(old_job_dir)):
            logging.debug("Substituting old job dir")
            out_file_path = out_file_path.replace(old_job_dir, job_dir)
        else:
            logging.warn("Not substituting the old job dir...")

        if (None == out_file_path):
            logging.error("Not found output file for the " \
                          "script %s." % bash_script_path)
            continue
        if (not os.path.isfile(out_file_path)):
            logging.error("Output log for %s not " \
                          "found! skipping it\nFile was: %s\n" % (bash_script_path, out_file_path))
            continue

        if pl == None:
            pl = ProcessLog(db, old_graph_dir)
        pl.process_job_out(out_file_path)


    if pl is not None:
        pl._write_list(pl.iso_list)


if __name__ == '__main__':
    main()



# Script used to check the status of the extraction
#
# The script collects the number of:
#   - dowloaded repos
#   - built repos
#   - graph extracted
#

import sys
import os
import json
import optparse

STATUS_FILE_NAME="repo_status.json"
STATUS_DEPTH=3

class LogStats:
    down,built,extr,done = range(4)
    status_vect = [down,built,extr,done]

detailed_errors = ["Cannot find application",
                   "Cannot find classes.jar",
                   "Cannot find the jar for"]

def get_logs(repo_folder):
    """ Get the list of logs """
    def get_status(path, depth, statuses):
        if depth == 3:
            for f in os.listdir(path):
                if f == STATUS_FILE_NAME:
                    f = os.path.join(path,f)
                    statuses.append(f)
        else:
            for d in os.listdir(path):
                d = os.path.join(path,d)
                if not os.path.isdir(d): continue
                get_status(d, depth + 1, statuses)
    statuses = []
    get_status(repo_folder, 0, statuses)
    return statuses

def init_res():
    res = {}
    for s in LogStats.status_vect: res[s] = []
    return res

def process_log(app_log_path, log_file, res, details):
    with open(log_file, "r") as f:
        def _get_app_log(app_log_path, log_file):
            splitted = log_file.split("/")
            assert (len(splitted) > 5)
            assert (splitted[len(splitted)-1] == STATUS_FILE_NAME)
            un_repo = splitted[(len(splitted) - 4) : (len(splitted) - 2)]
            result = "repo_log_%s_%s_.log" % (un_repo[0], un_repo[1])
            result = os.path.join(app_log_path, result)
            return result

        data = json.load(f)
        assert ("status" in data and "description" in data)

        status = data["status"]
        assert len(LogStats.status_vect) > status
        res[LogStats.status_vect[status]].append(log_file)

        if (status == 2):
            # Stuck at extraction
            app_log_file = _get_app_log(app_log_path, log_file)

            if (not os.path.isfile(app_log_file)):
                print "WARNING: app log file %s for %s repo not found!" % (app_log_file, log_file)
            else:
                with open(app_log_file) as app_log:
                    error = None
                    for l in app_log.readlines():
                        for de in detailed_errors:
                            l = l.strip()
                            if (l.startswith(de)):
                                error = de
                    if error == None:
                        print "Unknown error for %s" % (app_log_file)
                    else:
                        if error not in details:
                            details[error] = []
                        details[error].append(log_file)


def print_stats(res, details):
    print "--- Stats ---"
    for s in LogStats.status_vect:
        print "%s: %d repos" % (s, len(res[s]))

    print "List of repos"
    for s in LogStats.status_vect:
        print "Status: %d" % s
        for repo in res[s]:
            print repo
        print "----"

    print "Detailed errors"
    for error in details.keys():
        print "%s: %d" % (error, len(details[error]))

def main():
    p = optparse.OptionParser()
    p.add_option('-s', '--repofolder', help="Root of the repos")
    p.add_option('-l', '--applogfolder', help="Folder that contains the application logs")    

    def usage(msg=""):
        if msg:
            print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)

    opts, args = p.parse_args()
    if not opts.repofolder:
        usage("Missing repo folder")
    if not os.path.isdir(opts.repofolder):
        usage("%s is not a directory!" % opts.repofolder)
    if not opts.applogfolder:
        usage("Missing log folder")
    if not os.path.isdir(opts.applogfolder):
        usage("%s is not a directory!" % opts.applogfolder)
    logs = get_logs(opts.repofolder)

    res = init_res()
    details = {}
    for log in logs: process_log(opts.applogfolder, log, res, details)
    print_stats(res,details)

if __name__ == '__main__':
    main()

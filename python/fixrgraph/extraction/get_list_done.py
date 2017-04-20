import sys
import os
import stat
import optparse
import logging
import shutil
import json
import re
import string

def main():
    p = optparse.OptionParser()
    p.add_option('-i', '--input', help="Input file")
    p.add_option('-o', '--output', help="Output file")
    p.add_option('-s', '--status', help="Status to search for (0,1,2,3)")

    def usage(msg=""):
        if msg:
            print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)

    opts, args = p.parse_args()
    if (not opts.input): usage("No input")
    if (not opts.output): usage("No output")
    if (not opts.status): usage("No status")
    if (not os.path.isfile(opts.input)): usage("Input file does not existsnot")


    repo_list = []
    with open(opts.input, "r") as f:
        data = json.load(f)
        assert "repo_status" in data
        for json_repo in data["repo_status"]:
            assert "status" in json_repo
            if str(json_repo["status"]) == opts.status:
                assert "repo" in json_repo

                all_string = json_repo["repo"]
                splitted = all_string.split("|")
                assert (3 == len(splitted))

                repo_list.append(all_string)

        f.close()

    with open(opts.output, "w") as fout:
        repo_status = [ {"repo" : x, "status" : opts.status} for x in repo_list]
        repo_list = [ {"repo" : x} for x in repo_list]
        json_elem = {"repo_list" : repo_list, "repo_status" : repo_status}

        print "Found %d repos in status %s" % (len(repo_status), opts.status)
        json.dump(json_elem, fout)

        fout.close()


if __name__ == '__main__':
    main()

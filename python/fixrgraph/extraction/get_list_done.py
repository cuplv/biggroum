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

    def usage(msg=""):
        if msg:
            print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)

    opts, args = p.parse_args()
    if (not opts.input): usage("No input")
    if (not opts.output): usage("No output")
    if (not os.path.isfile(opts.input)): usage("Input file does not existsnot")


    with open(opts.input, "r") as f:
        data = json.load(f)
        assert "repo_status" in data
        for json_repo in data["repo_status"]:
            assert "status" in json_repo
            if json_repo["status"] == 3:
                assert "repo" in json_repo

                all_string = json_repo["repo"]
                splitted = all_string.split("|")
                assert (3 == len(splitted))

                username = splitted[0]
                reponame = splitted[1]
                commit = splitted[2]

                reposuffix = "%s/%s/%s" % (username, reponame, commit)
                src = "/media/data/2016_10_28_extraction/%s" % reposuffix
                dst = "/media/data/groum_sources/%s" % reposuffix

                print ("mkdir %s" % dst)
                print ('rsync -zarv --include="*/" --include="*.java" --exclude="*" %s %s' % (src, dst))

if __name__ == '__main__':
    main()

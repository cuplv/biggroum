import argparse
import fnmatch
import os
import sys
from fixrgraph.extraction.run_extractor import (
    RepoProcessor,
    RepoErrorLog
)

def findFiles(base_dir, extension):
    matches = []
    for root, dirnames, filenames in os.walk(base_dir):
        for filename in fnmatch.filter(filenames, '*.%s' % extension):
            matches.append(os.path.join(root, filename))
    return matches

def find_class_files(base_dir):
    all_class_files = findFiles(base_dir,"class")
    dirs = set()
    for cf in all_class_files:
        classesdirs = ["classes", "kotlin-classes"]
        # TODO: hardcoded method to find class directory, this needs to be fixed!
        # TODO: refactor to use apk file to avoid this
        for classesdir in classesdirs:
            if(classesdir in cf):
                spl = cf.split(os.path.sep + classesdir + os.path.sep)
                if(len(spl) > 0):
                    ncf = os.path.join(spl[1],classesdir)
                    dirs.add(ncf)
    return dirs


class BuildInfoClassList:
    def __init__(self, classes, jars):
        self.classes = classes
        self.jars = jars

def extract_single_class_dir(repo, out_dir, extractor_jar, path, filter=None, repo_logger = None):

    assert (repo_logger is None or isinstance(repo_logger, RepoErrorLog))

    build_info = BuildInfoClassList(find_class_files(path), [])

    graph_dir_path = os.path.join(out_dir, "graphs")
    prov_dir_path = os.path.join(out_dir, "provenance")
    RepoProcessor.extract_static(
        repo,
        repo_logger,
        # indir is used when we do not have the build_info
        # object --- here we have one
        None,
        os.environ['ANDROID_HOME'], # TODO: pass from outside, not rely on env variables
        graph_dir_path,
        prov_dir_path,
        "",
        extractor_jar,
        build_info,
        path,
        filter
    )

class BuildInfoApk:
    def __init__(self, apk):
        self.apks = [apk]
def extract_single_apk(repo, out_dir, extractor_jar, path, filter=None, repo_logger=None):
    assert (repo_logger is None or isinstance(repo_logger, RepoErrorLog))
    apk_list = findFiles(path, "apk")
    apk_list.reverse()
    graph_dir_path = os.path.join(out_dir, "graphs")
    prov_dir_path = os.path.join(out_dir, "provenance")
    for apk in apk_list:
        build_info = BuildInfoApk(apk)
        RepoProcessor.extract_static_apk(repo,
                                         repo_logger,
                                         os.environ['ANDROID_HOME'],
                                         graph_dir_path,
                                         prov_dir_path,
                                         extractor_jar,
                                         build_info,
                                         path,
                                         filter)
        return # Only extract one apk file
    sys.stderr.write("Error: No apk file found in directory: %s\n" % path)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Extract groums from single directory.")
    p.add_argument('-d', '--app_directory', help="Built directory containing app", required=True)
    p.add_argument('-g', '--graphdir', help="Directory that will contain the generated graphs", required=True)
    p.add_argument('-o', '--organization', help="Github or Bitbucket username of organization", required=True)
    p.add_argument('-n', '--app_name', help="Github or Bitbucket name of app.", required=True)
    p.add_argument('-a', '--hash', help="Git hash of current version", required=True)
    p.add_argument('-j', '--extractorjar', help="Jar file of the extractor (it must contain ALL the dependencies)",
                 required=True)
    p.add_argument('-f', '--filter', help="Colon separated list of java files for symbols to extract", required=False)
    p.add_argument('-p', '--use_apk',
                   help="Extract from apk file, can take a directory or a specific apk", action='store_true')
    args = p.parse_args()

    if args.use_apk:
        extract_single_apk([args.organization, args.app_name, args.hash],
                           args.graphdir,
                           args.extractorjar,
                           args.app_directory,
                           args.filter)
    else:
        extract_single_class_dir([args.organization, args.app_name, args.hash],
                             args.graphdir,
                             args.extractorjar,
                             args.app_directory,
                             args.filter)

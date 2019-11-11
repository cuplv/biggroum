import argparse
import fnmatch
import os
import run_extractor
import tempfile

# MIN_HEAP_SIZE="1024m"
# MAX_HEAP_SIZE="2048m"
# TIMEOUT="60"

def findFiles(base_dir, extension):
    matches = []
    for root, dirnames, filenames in os.walk(base_dir):
        for filename in fnmatch.filter(filenames, '*.%s' % extension):
            matches.append(os.path.join(root, filename))
    return matches

def find_class_files(base_dir):
    all_class_files = findFiles(base_dir,"class")
    #TODO: this logic is obviously bad and needs to be updated

    return all_class_files
    # candidate_directories = set()
    # for cf in all_class_files:
    #     spl = cf.split("/classes/")
    #     if len(spl) > 1:
    #         candidate_directories.add(spl[0])
    # if len(candidate_directories) == 0:
    #     return None
    #
    # return [c for c in all_class_files if c.startswith(candidate_directories[0])]

def isGeneratedFile(file_path):
    if "app/build/generated/" in file_path:
        return True
    fname = file_path.split(os.path.sep)[-1] 
    if fname == "R.java":
        return True
    if fname == "BuildConfig.java":
        return True

def find_rt_jar():
    rtjar_file = None
    for rtloc in ["jre/lib/rt.jar", "/lib/jvm/java-8-openjdk-amd64/jre/lib/rt.jar"]:
        rtjar_file = os.path.join(os.environ['JAVA_HOME'],rtloc)
        print(rtjar_file)
        if os.path.exists(rtjar_file):
            break
    if rtjar_file is None:
        raise Exception("java runtime 'rt.jar' file not found")
    return rtjar_file

class BuildInfoSimple:
    def __init__(self, classes, jars):
        self.classes = classes
        self.jars = jars
def extract_simple_class(repo, out_dir,extractor_jar,path,filter=None):

    build_info = BuildInfoSimple(find_class_files(path), [])

    graph_dir_path = os.path.join(out_dir, "repo_graph_dir")
    prov_dir_path = os.path.join(out_dir, "repo_prov_dir")
    run_extractor.RepoProcessor.extract_static(
        repo = repo,
        log=None, # TODO: retain log somewhere?
        in_dir=None, #TODO: this doesn't seem to do anything
        android_home=os.environ['ANDROID_HOME'],
        graph_dir=graph_dir_path,
        prov_dir=prov_dir_path,
        classpath="",
        extractor_jar=extractor_jar,
        build_info=build_info,
        buildable_repos_path=path,
        file_filter=filter
    )


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
    args = p.parse_args()


    extract_simple_class(repo = [args.organization,args.app_name,args.hash],
                         out_dir=args.graphdir,
                         extractor_jar=args.extractorjar,
                         path=args.app_directory,
                         filter=args.filter)
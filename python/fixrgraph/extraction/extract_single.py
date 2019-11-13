import argparse
import fnmatch
import os
import run_extractor

def findFiles(base_dir, extension):
    matches = []
    for root, dirnames, filenames in os.walk(base_dir):
        for filename in fnmatch.filter(filenames, '*.%s' % extension):
            matches.append(os.path.join(root, filename))
    return matches

def find_class_files(base_dir):
    all_class_files = findFiles(base_dir,"class")
    #TODO: this logic will probably fail on some repos but works for simple things
    return all_class_files

def isGeneratedFile(file_path):
    if "app/build/generated/" in file_path:
        return True
    fname = file_path.split(os.path.sep)[-1] 
    if fname == "R.java":
        return True
    if fname == "BuildConfig.java":
        return True

def find_rt_jar():
    for rtloc in ["jre/lib/rt.jar", "/lib/jvm/java-8-openjdk-amd64/jre/lib/rt.jar"]:
        rtjar_file = os.path.join(os.environ['JAVA_HOME'],rtloc)
        print(rtjar_file)
        if os.path.exists(rtjar_file):
            break
    if rtjar_file is None:
        raise Exception("java runtime 'rt.jar' file not found")
    return rtjar_file

class BuildInfoClassList:
    def __init__(self, classes, jars):
        self.classes = classes
        self.jars = jars
def extract_single_class_dir(repo, out_dir, extractor_jar, path, filter=None, logger=None):

    build_info = BuildInfoClassList(find_class_files(path), [])

    graph_dir_path = os.path.join(out_dir, "graphs")
    prov_dir_path = os.path.join(out_dir, "provenance")
    run_extractor.RepoProcessor.extract_static(
        repo = repo,
        log=logger,
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


    extract_single_class_dir(repo = [args.organization, args.app_name, args.hash],
                             out_dir=args.graphdir,
                             extractor_jar=args.extractorjar,
                             path=args.app_directory,
                             filter=args.filter)
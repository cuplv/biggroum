# Script used to run the graph extractor on a list of repositories.
#
# WARNING: the script is derived from the one wrote for ScanR (https://github.com/cuplv/Scanr/scripts/run_scanr.py)
#
# Both scripts should be merged at some point and made general enough.
#
# The script performs different phases:
#   0. Download the repos
#   1. Build a app
#   2. Run the graph extractor
#

# Get dependencies from gradle
#   - get all the compile dependencies of the app
#

import sys
import os
import stat
import optparse
import logging
import traceback
import shutil
import json
import subprocess
import re
import traceback
import string
from xml.dom.minidom import parse, parseString

MIN_STATUS = 2
MIN_HEAP_SIZE="1024m"
MAX_HEAP_SIZE="10000m"
TIMEOUT="60"

tasks_list = ["download", "build", "extract"]


def get_repo_status_file_name(repo_path):
    return os.path.join(repo_path, "repo_status.json")


class RepoStatus:
    """Serialize the "status" of the repo processing using json.
    The status represent the current activity to run.
    """
    Download, Build, Extract, Done = range(4)

    status2task = {Download: "download",
                   Build: "build",
                   Extract: "extract",
                   Done: "done"}

    def __init__(self, file_name=None):
        self.status = RepoStatus.Download
        self.description = self.status2task[self.status]
        self.file_name = file_name
        if None != file_name:
            self._read_status_from_file_(file_name)

    def _read_status_from_file_(self, file_name):
        with open(file_name, "r") as f:
            data = json.load(f)
            assert ("status" in data)
            self.status = data["status"]
            if "description" in data:
                self.description = data["description"]
                # Both the numeric status and the description should be the same
                # assert(self.description == self.status2task[self.status])

    def set_file_name(self, file_name):
        self.file_name = file_name

    def write_on_file(self):
        assert (self.file_name != None)
        with open(self.file_name, "w") as f:
            json.dump({"status": self.status, "description" : self.description}, f)


    def next(self):
        if self.status != RepoStatus.Done:
            self.status = self.status + 1
            self.description = self.status2task[self.status]

class ErrorLog:
    """Keeps a list of error messages separated per repo.
    """

    def __init__(self):
        self.log = {}  # map from repo to a list of errors

    def _get_list_(self, repo):
        if repo not in self.log:
            err_list = []
            self.log[repo] = err_list
        return self.log[repo]

    def add_error(self, repo, error_msg):
        err_list = self._get_list_(repo)
        err_list.append(error_msg)

    def get_errors(self, repo):
        err_list = self._get_list_(repo)
        return err_list

    def hasError(self, repo):
        if repo in self.log:
            return len(self.log[repo]) > 0
        return False

    def printErrorRepo(self, repo, outStream):
        outStream.write("Repo %s\n" % str(repo))
        for error in self.log[repo]:
            outStream.write("%s\n" % str(error))
            outStream.write("\n")

    def printErrors(self, outStream):
        for key, val in self.log.iteritems():
            outStream.write("Repo %s\n" % str(key))
            for error in val:
                outStream.write("%s\n" % str(error))
            outStream.write("\n")


def read_repo(repo_file):
    """Read the repo_file as a json file and returns a list of couples.
    """
    """A couple contains the user_name and the repo name
    """
    res = []
    repos_list = json.loads(repo_file.read())
    for repo in repos_list:
        assert "user_name" in repo and "repo_name" in repo
        if ("hash" in repo):
            res.append((repo["user_name"], repo["repo_name"], repo["hash"]))
        else:
            res.append((repo["user_name"], repo["repo_name"]))
    return res


class RepoProcessor:
    """Implements the different phases needed to process the repos
    """

    def __init__(self, in_dir, graph_dir, prov_dir, slice_filter,
                 extractor_jar, classpath):
        # Keeps the error log for each repo
        self.log = ErrorLog()
        # Directory where download the repositories
        self.in_dir = in_dir
        self.graph_dir = graph_dir
        self.prov_dir = prov_dir
        self.slice_filter = slice_filter
        self.extractor_jar = extractor_jar
        self.classpath = classpath

        if 'ANDROID_HOME' not in os.environ:
            self.log.add_error(repo, "ANDROID_HOME path is not set")
            assert False
        else:
            self.android_home = os.environ['ANDROID_HOME']

    @staticmethod
    def get_repo_url(user_name, repo_name):
        repo_url = "https://github.com/%s/%s" % (user_name, repo_name)
        return repo_url

    @staticmethod
    def get_repo_path(dir_path, repo):
        """Return the path of the repository relative to dir_path.
        dir_path is either the input or the output directory.
        """
        if(len(repo) > 2):
            repo_path = os.path.join(dir_path, repo[0], repo[1],repo[2])
        else:
            repo_path = os.path.join(dir_path, repo[0], repo[1], "head")
        return repo_path

    @staticmethod
    def get_repo_name(repo):
        return "%s/%s" % (repo[0], repo[1])

    def _call_sub(self, repo, args, cwd=None, wait=True):
        """Call a subprocess.
        """
        logging.info("Executing %s" % " ".join(args))

        # not pipe stdout - processes will hang
        # Known limitation of Popen
        proc = subprocess.Popen(args, cwd=cwd)
        proc.wait()

        return_code = proc.returncode
        if (return_code != 0):
            err_msg = "Error code is %s\nCommand line is: %s\n%s" % (str(return_code), str(" ".join(args)),
                                                                     "\n")
            self.log.add_error(repo, err_msg)
            logging.error("Error executing %s\n%s" % (" ".join(args), err_msg))
            return False

        return True


    def download(self, repo):
        """Dowload the repository."""
        logging.info("Download task for repo: " + str(repo))

        try:
            import pygit2
        except Exception as e:
            logging.error("Error importing pygit2.")
            print "Error importing pygit2."
            self.log.add_error(repo, e.message)
            return None

        repo_url = RepoProcessor.get_repo_url(repo[0], repo[1])
        repo_folder = RepoProcessor.get_repo_path(self.in_dir, repo)

        try:
            logging.debug("Downloading %s" % (repo_url))

            if(os.path.exists(repo_folder)):
                shutil.rmtree(repo_folder)
            repository = pygit2.clone_repository(repo_url,
                                                 repo_folder,
                                                 bare=False, repository=None, remote=None,
                                                 checkout_branch=None)
            if(len(repo) > 2):
                # If the repository information has an hash, reset to that version
                logging.debug("Reset %s to hash %s" % (repo_url, repo[2]))
                repository.reset(repo[2], pygit2.GIT_RESET_HARD)
            logging.debug("Downloaded %s" % (repo_url))

        except Exception as e:
            traceback.print_exc()
            print "Error processing %s" % (repo_url)
            logging.error("Error processing %s" % (repo_url))
            self.log.add_error(repo, e.message)
            return None

        return repo

    def find_gradle_file(self, repo_folder):
        """Find the build.gradle file in the repository.
        Return either the path to a build.gradle file or None.
        """
        gradle_build_name = "build.gradle"

        for root, dirs, files in os.walk(repo_folder, topdown=True):
            if gradle_build_name in files:
                return os.path.join(root, gradle_build_name)

        return None

    """Get the min/max SDK version used by the app."""
    def matchNumber(self, key, startstring):
        key = key.strip()
        startstring = startstring.strip()
        if not startstring.startswith(key):
            return None
        match = re.search('^%s ([0-9]+)' % key, (startstring))
        if match:
            number = match.group(1)
            return int(number)
        return None

    def get_version_from_gradle(self, gradle_build_file):

        def getLimit(current, new, is_min):
            if (is_min and new != None and
                    (new < current or current == None)):
                return new
            if (is_min and new != None and
                    (new > current or current == None)):
                return new
            return current

        android_version = None
        min_sdk_version = None
        max_sdk_version = None

        with open(gradle_build_file, 'r') as f:
            for l in f.readlines():
                new_min = self.matchNumber("minSdkVersion", l)
                new_max = self.matchNumber("maxSdkVersion", l)

                match = re.search('^compileSdkVersion ([0-9]+)', l.strip())
                if match:
                    version_number =  match.group(1)
                else:
                    version_number = None

                min_sdk_version = getLimit(min_sdk_version, new_min, True)
                max_sdk_version = getLimit(max_sdk_version, new_max, False)
                if (version_number != None):
                    android_version = version_number

        return (min_sdk_version, max_sdk_version, android_version)

    def getGradleInfo(self, repo, repo_folder):
        # Current heuristic to build an android app
        # 1. Find the build.gradle file (find the first in the repo tree)
        #
        # Decision making:
        #   - we need to find at least one build.gradle
        #

        gradle_build_file = self.find_gradle_file(repo_folder)
        if (None == gradle_build_file):
            return (None, None)

        gradle_path = os.path.dirname(gradle_build_file)

        return (gradle_build_file, gradle_path)

    def build(self, repo):
        """Build the repo.
        """
        logging.debug("Building %s/%s" % (repo[0], repo[1]))

        repo_folder = RepoProcessor.get_repo_path(self.in_dir, repo)
        assert (os.path.exists(repo_folder))

        (gradle_build_file, gradle_path) = self.getGradleInfo(repo, repo_folder)
        if (None == gradle_build_file):
            # Skip if there is no build.gradle
            self.log.add_error(repo, "Gradle file not found found.")
            logging.error("Gradle file not found found for %s." % str(repo))
            return None
        else:
            logging.info("Found gradle file %s for repo %s" % (gradle_build_file, str(repo)))

        # Skip if the API version is not <= 17
        # (min_apk, max_apk, version_number) = self.get_version_from_gradle(gradle_build_file)

        # run the compilation with gradle
        gradlew_path = os.path.join(gradle_path, "gradlew")
        if os.path.exists(gradlew_path):
            compile_cmd = gradlew_path
            if (not os.access(gradlew_path, os.X_OK)):
                os.chmod(gradlew_path, stat.S_IEXEC | stat.S_IREAD)
        else:
            compile_cmd = "gradle"

        try:
            is_ok = self._call_sub(repo, [compile_cmd, "--stacktrace",
                                          "-p", gradle_path, "assembleDebug"])
            if not is_ok:
                msg = "call_sub ended in error for %s/%s" % (repo[0], repo[1])
                logging.debug(msg)
                self.log.add_error(repo, msg)
                return None

        except Exception as e:
            logging.debug("Cannot build %s/%s" % (repo[0], repo[1]))
            self.log.add_error(repo, e.message)
            return None

        logging.debug("Build end for %s/%s" % (repo[0], repo[1]))
        return repo

    def getAndroidAppPlugin(self, repo, repo_folder):
        gradle_build_name = "build.gradle"

        (gradle_build_file, basePath) = self.getGradleInfo(repo, repo_folder)
        if (None == gradle_build_file):
            # Skip if there is no build.gradle
            self.log.add_error(repo, "Gradle file found.")
            return None

        assert (os.path.exists(basePath))

        gradles_for_app = []
        for root, dirs, files in os.walk(basePath, topdown=True):
            if gradle_build_name in files:
                gradle_file = os.path.join(root, gradle_build_name)
                with open(gradle_file, 'r') as gradleFile:
                    for line in gradleFile:
                        if "com.android.application" in line:
                            gradles_for_app.append(gradle_file)
                            break

        if (len(gradles_for_app) < 1):
            msg = "No builds for app in %s/%s" % (repo[0], repo[1])
            logging.debug(msg)
            self.log.add_error(repo, msg)
        elif (len(gradles_for_app) > 1):
            gradles_for_app = [l for l in gradles_for_app if not "wear" in l]
            if (len(gradles_for_app) > 1):
                # Found more apps
                logging.debug("Found more builds for apps for %s/%s" % (repo[0], repo[1]))
                message = "Found more builds for apps for %s/%s" % (repo[0], repo[1])
                for g in gradles_for_app:
                    message = message + "\n" + g
                self.log.add_error(repo, message)
                return None

        if (len(gradles_for_app) > 0):
            gradle_path = os.path.dirname(gradles_for_app[0])
        else:
            return None
        return gradle_path

    # def search_classes(self, repo_folder):
    #     """Looks for the classes.jar file created during the build"""
    #     logging.info("Searching classes.jar in %s " + str(repo_folder))

    #     result = []
    #     for root, dirs, files in os.walk(repo_folder):
    #         if "classes.jar" in files:
    #             result.append(os.path.join(root, "classes.jar"))

    #     if len(result) > 0:
    #         # choose the debug one if it exists
    #         for r in result:
    #             if "debug" in r:
    #                 return r
    #         # return the first
    #         return result[0]
    #     else:
    #         return None

    def search_classes(self, repo_dir, gradle_file_path):
        """Looks for the classes.jar file created during the build"""
        logging.info("Searching main classes %s " + str(gradle_file_path))

        manifest = None
        for root, dirs, files in os.walk(gradle_file_path):
            if "AndroidManifest.xml" in files:
                manifest = os.path.join(root, "AndroidManifest.xml")

        if None != manifest:
            # get the package name manifest, package
            #
            # get the application, android:name tag
            #
            dom1 = parse(manifest)
            manifest_node = dom1.getElementsByTagName('manifest')
            if (len(manifest_node) > 0):
                if None != manifest_node[0].attributes and 'package' in manifest_node[0].attributes.keys():
                    packageName = str(manifest_node[0].attributes['package'].value)
                    # OS dependent
                    packagePath = packageName.replace(".", "/")

                    # search for package name and classes
                    classes = []
                    for root, dirs, files in os.walk(repo_dir):
                        if packagePath in str(root):
                            for f in files:
                                str_f = str(f)
                                if str_f.endswith(".class"):
                                    classes.append(os.path.join(root, f))

                    if len(classes) > 0:
                        for c in classes:
                            try:
                                c_str = str(c)
                                index = c_str.index(packagePath)
                                base_path = c_str[:index]
                                # pick the first one.
                                logging.debug("Base path for %s is %s" % (repo_dir,base_path))
                                return base_path
                            except ValueError:
                                # do nothing.
                                base_path = None
            logging.debug("Cannot find base path for %s" % (repo_dir))
            return None


    def get_android_jar(self, version):
        """Find the right android.jar"""
        jar_path = os.path.join(self.android_home, "platforms", "android-%s" % version, "android.jar")

        if not os.path.isfile(jar_path):
            msg = "Cannot find the jar %s" % (jar_path)
            logging.debug(msg)
            return None
        else:
            return jar_path

    def get_support_library(self, gradle_build_file, sdk_version):
        def add_lib(lib_list, sl):
            if os.path.isfile(sl):
                lib_list.append(sl)
            else:
                logging.debug("Support library %s not found!", sl)
            return lib_list

        lib_list = []
        template = "./extras/android/m2repository/com/android/support/support-${sup_version}/${version}/support-${sup_version}-${version}-sources.jar"


        dots = 0
        for c in sdk_version:
            if c == ".": dots = dots + 1
            assert dots <= 2
        if (dots <= 1):
            sdk_version = sdk_version + ".0"
            if (dots <= 2): sdk_version = sdk_version + ".0"

        # with open(gradle_build_file, 'r') as f:
        #     for l in f.readlines():
        #         l = l.strip()
        #         match = re.search('compile \'com.android.support:appcompat-(v[0-9]*):([0-9\.]*)\'', l)
        #         if None != match:
        #             sup_version  = match.group(1)
        #             sdk_version = match.group(2)

        #             lib = string.Template(template).safe_substitute({"version" : sdk_version, "sup_version" : sup_version})
        #             lib_list.append(lib)

        #with open(gradle_build_file, 'r') as f:
        #    for l in f.readlines():
        for sup_version in ["v4","v7","v13"]:
                    #l = l.strip()
                    #match = re.search('compile \'com.android.support:appcompat-(v[0-9]*):([0-9\.]*)\'', l)
                    #if None != match:
            lib = string.Template(template).safe_substitute({"version" : sdk_version, "sup_version" : sup_version})
            lib = os.path.join(self.android_home, lib)
            lib_list = add_lib(lib_list, lib)

        support_libs = ["extras/android/support/percent/libs/android-support-percent.jar",
                        "extras/android/support/graphics/drawable/libs/android-support-vectordrawable.jar",
                        "extras/android/support/graphics/drawable/libs/android-support-animatedvectordrawable.jar",
                        "extras/android/support/recommendation/libs/android-support-recommendation.jar",
                        "extras/android/support/v17/leanback/libs/android-support-v17-leanback.jar",
                        "extras/android/support/v17/preference-leanback/libs/android-support-v17-preference-leanback.jar",
                        "extras/android/support/annotations/android-support-annotations.jar",
                        "extras/android/support/customtabs/libs/android-support-customtabs.jar",
                        "extras/android/support/v14/preference/libs/android-support-v14-preference.jar",
                        "extras/android/support/design/libs/android-support-design.jar",
                        "extras/android/support/multidex/instrumentation/libs/android-support-multidex-instrumentation.jar",
                        "extras/android/support/multidex/instrumentation/libs/android-support-multidex.jar",
                        "extras/android/support/multidex/library/libs/android-support-multidex.jar",
                        "extras/android/support/v4/android-support-v4.jar",
                        "extras/android/support/v13/android-support-v13.jar",
                        "extras/android/support/v7/recyclerview/libs/android-support-v7-recyclerview.jar",
                        "extras/android/support/v7/cardview/libs/android-support-v7-cardview.jar",
                        "extras/android/support/v7/appcompat/libs/android-support-v4.jar",
                        "extras/android/support/v7/appcompat/libs/android-support-v7-appcompat.jar",
                        "extras/android/support/v7/palette/libs/android-support-v7-palette.jar",
                        "extras/android/support/v7/mediarouter/libs/android-support-v7-mediarouter.jar",
                        "extras/android/support/v7/preference/libs/android-support-v7-preference.jar",
                        "extras/android/support/v7/gridlayout/libs/android-support-v7-gridlayout.jar"]
        for sl in support_libs:
            sl = os.path.join(self.android_home, sl)
            lib_list = add_lib(lib_list, sl)

        return lib_list

    def extract(self, repo):
        """Extract the graph for repo."""
        logging.info("Extracting graphs for repo: " + str(repo))

        repo_folder = RepoProcessor.get_repo_path(self.in_dir, repo)

        app_gradle_file_path =self.getAndroidAppPlugin(repo, repo_folder)
        if None == app_gradle_file_path:
            # Error, classes.jar not found
            msg = "Cannot find application build.gradle file for %s/%s" % (repo[0], repo[1])
            logging.debug(msg)
            self.log.add_error(repo, msg)
            return None

        app_gradle_file = os.path.join(app_gradle_file_path, "build.gradle")
        logging.debug("App gradle file is %s" % app_gradle_file)
        (min_apk, max_apk, version_number) = self.get_version_from_gradle(app_gradle_file)

        # get jar file from the android sdk
        android_jar_path = self.get_android_jar(version_number)
        if None == android_jar_path:
            msg = "Cannot find the jar for %s/%s" % (repo[0], repo[1])
            logging.debug(msg)
            self.log.add_error(repo, msg)
            return None

        # set the process_dir: we look for the classes.jar file created
        # during the build.
        process_dir = self.search_classes(repo_folder, app_gradle_file_path)

        if None == process_dir:
            # Error, classes.jar not found
            logging.debug("Cannot find classes.jar for %s/%s" % (repo[0], repo[1]))
            self.log.add_error(repo, "Cannot find classes.jar for %s/%s" % (repo[0], repo[1]))
            return None

        # Small try on support libraries
        # android_support_library_path = self.get_support_library(app_gradle_file, version_number)
        # for l in android_support_library_path:
        #     android_jar_path = android_jar_path + ":" + l
        logging.debug("Android jar path: %s for %s/%s" % (android_jar_path, repo[0], repo[1]))

        try:
            repo_graph_dir = RepoProcessor.get_repo_path(self.graph_dir, repo)
            if not os.path.isdir(repo_graph_dir): os.makedirs(repo_graph_dir)

            repo_prov_dir = RepoProcessor.get_repo_path(self.prov_dir, repo)
            if not os.path.isdir(repo_prov_dir): os.makedirs(repo_prov_dir)

            additional_cp = android_jar_path + ":" + process_dir
            if self.classpath != None:
                classpath = self.classpath + ":" + additional_cp
            else:
                classpath = additional_cp

            repo_url = RepoProcessor.get_repo_url(repo[0], repo[1])
            args = ["java",
                    "-Xms%s" % MIN_HEAP_SIZE,
                    "-Xmx%s" % MAX_HEAP_SIZE,
                    "-jar", self.extractor_jar,
                    "-s", "false", # we read bytecode
                    "-l", classpath,
                    "-p", process_dir,
                    "-o", repo_graph_dir,
                    "-d", repo_prov_dir,
                    "-j", "true", # enable jphantom
                    "-z", repo_folder,
                    "-t", TIMEOUT,
                    "-n", repo[0],
                    "-r", repo[1],
                    "-u", repo_url]
            if len(repo) > 2:
                args.append("-h")
                args.append(repo[2])
            is_ok = self._call_sub(repo, args)
            if not is_ok:
                msg = "call_sub ended in error for %s/%s" % (repo[0], repo[1])
                logging.debug(msg)
                self.log.add_error(repo, msg)
                return None

        except Exception as e:
            # DEBUG
            logging.debug("Cannot extract the graphs from %s/%s" % (repo[0], repo[1]))
            self.log.add_error(repo, e.message)
            return None

        logging.debug("Extraction of graph ended for %s/%s" % (repo[0], repo[1]))
        return repo


    def processFromStep(self, repo_list, step):
        tasks = {"download": self.download,
                 "build": self.build,
                 "extract" : self.extract}

        assert (step in tasks)
        assert None != tasks_list
        index = tasks_list.index(step)
        steps_to_do = tasks_list[index:]

        repo_index = 1
        tot_repos = len(repo_list)
        for repo in repo_list:
            logging.info("Repo %d/%d..." % (repo_index, tot_repos))
            logging.info("Repo %s" % RepoProcessor.get_repo_name(repo))

            # read the status of the repo
            repo_folder = RepoProcessor.get_repo_path(self.in_dir, repo)
            repo_status_fn = get_repo_status_file_name(repo_folder)
            if (os.path.isfile(repo_status_fn)):
                logging.debug("Repo status exists for %s" % RepoProcessor.get_repo_name(repo))
                repoStatus = RepoStatus(repo_status_fn)
            else:
                logging.debug("Repo status does NOT exist for %s" % RepoProcessor.get_repo_name(repo))
                repoStatus = RepoStatus()
                repoStatus.set_file_name(repo_status_fn)

            if repoStatus.status < MIN_STATUS:
                logging.warning("Skipping repo %s (repo status %d < min status %d" %
                                (RepoProcessor.get_repo_name(repo), repoStatus.status, MIN_STATUS))
                continue

            repo_step_list = []
            found_status = False
            currentTask = RepoStatus.status2task[repoStatus.status]
            for l in steps_to_do:
                if l == currentTask:
                    found_status = True
                if found_status:
                    repo_step_list.append(l)

            # execute the sequence of tasks
            for task in repo_step_list:
                logging.info("Executing %s..." % task)
                f = tasks[task]
                try:
                    repo = f(repo)
                except Exception as e:
                    logging.info("Execution broken at %s." % task)
                    traceback.print_exc()

                if repo is None:
                    logging.info("Execution broken at %s." % task)
                    break
                else:
                    # set the status of the repo
                    repoStatus.next()
                    repoStatus.write_on_file()
            repo_index = repo_index + 1

    def printErrors(self, out):
        self.log.printErrors(out)


def main():
    p = optparse.OptionParser()
    p.add_option('-a', '--applist', help="List of android app")
    p.add_option('-i', '--indir', help="Directory used to download the repos")

    # Extractor options
    p.add_option('-g', '--graphdir', help="Directory that will contain the generated graphs")
    p.add_option('-p', '--provdir', help="Directory that will contain the provenance information")
    p.add_option('-f', '--filter', help="Comma separated list of packages that will be used as seeds in the slicing")
    p.add_option('-j', '--extractorjar', help="Jar file of the extractor (it must contain ALL the dependencies)")
    p.add_option('-l', '--classpath', help="Comma separated classpath used by the extractor - (i.e. add the android jar here)")

    p.add_option('-s', '--step', type='choice',
                 choices=["download", "build", "extract"],
                 help="Select the mode of usage", default="download")

    def usage(msg=""):
        if msg:
            print "----"
            print msg
            print "----\n"
        p.print_help()
        sys.exit(1)

    # parameter validation

    opts, args = p.parse_args()
    required = [opts.applist, opts.indir, opts.graphdir, opts.step]
    required_desc = ["--applist", "--indir", "--graphdir", "--step"]
    assert (len(required_desc) == len(required))
    for i in range(len(required)):
        if not required[i]: usage("Missing option %s" % required_desc[i])

    must_exist = [opts.applist, opts.extractorjar]
    for i in range(len(must_exist)):
        if not os.path.exists(must_exist[i]):
            usage("The file %s does not exists!" % must_exist[i])

    if None != opts.classpath:
        for jarfile in opts.classpath.split(":"):
            if not os.path.exists(jarfile):
                usage("The jar file %s specified in the classpath does not exists!" % jarfile)

    # end of parameter validation

    # create the indir, graphdir and provdir if they do not exist
    new_dir = [opts.indir, opts.graphdir, opts.provdir]
    for d in new_dir:
        if not os.path.isdir(d):
            try:
                os.mkdir(d)
            except OSError as e:
                traceback.print_exc()
                sys.exit(1)

    try:
        with open(opts.applist, 'r') as app_list_file:
            repo_list = read_repo(app_list_file)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

    # process the repos
    repoProcessor = RepoProcessor(opts.indir, opts.graphdir,
                                  opts.provdir, opts.filter,
                                  opts.extractorjar, opts.classpath)
    repoProcessor.processFromStep(repo_list, opts.step)

    try:
        for repo in repo_list:
            if repoProcessor.log.hasError(repo):
                repo_name = str(repo[0] + "_" + repo[1])
                repo_name = repo_name.replace("/", "_")
                commit_hash = repo[2] if (len(repo)>2)  else ""
                logfile = "repo_log_%s_%s.log" % (repo_name, commit_hash)

                with open(logfile , 'w') as out_file:
                    repoProcessor.log.printErrorRepo(repo, out_file)
                    out_file.flush()
                    out_file.close()

    except Exception as e:
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    log_name = "extraction_log_" + str(os.getpid())
    logging.basicConfig(filename = log_name, level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)

    file_to_check = []
    for f in file_to_check:
        logging.info("Searching for file %s" % f)
        assert(os.path.isfile(f))

    main()

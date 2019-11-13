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
import traceback
import string

try:
    import Queue as Queue
except ImportError:
    import queue as Queue

import threading
import functools

from xml.dom.minidom import parse, parseString

from fixrgraph.extraction.extractor_utils import (
    get_android_jar,
    search_classes,
    get_repo_url,
    get_repo_path,
    get_repo_name,
    get_version_from_gradle,
    getGradleInfo,
    getAndroidAppPlugin,
    write_log
)

MIN_STATUS = 0
#MIN_HEAP_SIZE="256m"
# MAX_HEAP_SIZE="256m"
MIN_HEAP_SIZE="1024m"
MAX_HEAP_SIZE="2048m"
TIMEOUT="60"



class ExtractorStatus:
    Download, Build, Extract, Done = range(4)

    status2task = {Download: "download",
                   Build: "build",
                   Extract: "extract",
                   Done: "done"}

    task2status = {"download":Download,
                   "build":Build,
                   "extract":Extract,
                   "done": Done}

    tasks_list = ["download", "build", "extract", "done"]

    """ Keep the whole status of the extraction. """
    def __init__(self, file_name):
        self._repo_set = set()
        self._repo2status = {}
        self._repo2log = {}
        self._file_name = file_name

        self.lock = threading.Lock()

        if (self._file_name != None):
            self.load()

    def _get_init_status(self):
        final_task = ExtractorStatus.tasks_list[0]
        final_status = ExtractorStatus.task2status[final_task]
        return final_status

    def _get_final_status(self):
        first_task = ExtractorStatus.tasks_list[len(ExtractorStatus.tasks_list)-1]
        first_status = ExtractorStatus.task2status[first_task]
        return first_status

    def get_status(self, repo):
        with self.lock:
            status = None
            if repo not in self._repo_set:
                # new repo, insert it
                self._repo_set.add(repo)
                status = self._get_init_status()
                self._repo2status[repo] = status
            else:
                status = self._repo2status[repo]
            return status

    def next_status(self, repo):
        with self.lock:
            repo_status = self._repo2status[repo]
            last_status = self._get_final_status()
            if repo_status != last_status:
                repo_status = repo_status + 1
                self._repo2status[repo] = repo_status


    def load(self):
        """ Load the status """
        if os.path.isfile(self._file_name):
            input_file = open(self._file_name,'r')
            data = json.load(input_file)

            for r in data["repo_list"]:
                repo = self._read_repo(r)
                self._repo_set.add(repo)

            for json_status in data["repo_status"]:
                repo = self._read_repo(json_status)
                self._repo2status[repo] = json_status["status"]

            for json_status in data["repo_log"]:
                repo = self._read_repo(json_status)
                self._repo2log[repo] = json_status["log"]

    def write(self):
        """ Write the status """
        with self.lock:
            repo_list = []
            for repo in self._repo_set:
                repo_data = {}
                self._write_repo(repo_data, repo)
                repo_list.append(repo_data)

            repo2status = []
            for repo,status in self._repo2status.iteritems():
                repo_data = {}
                self._write_repo(repo_data, repo)
                repo_data["status"] = status
                repo2status.append(repo_data)

            repo2log = []
            for repo,log in self._repo2log.iteritems():
                repo_data = {}
                self._write_repo(repo_data, repo)
                repo_data["log"] = log
                repo2log.append(repo_data)

            with open(self._file_name, "w") as outfile:
                json.dump({"repo_list" : repo_list,
                           "repo_status" : repo2status,
                           "repo_log" : repo2log},
                          outfile);
                outfile.close()


    def _read_repo(self, json_data):
        with self.lock:
            repo_string = json_data["repo"]
            splitted = repo_string.split("|")
            user = splitted[0]
            repo_name = splitted[1]
            chash = splitted[2]
            return (user,repo_name,chash)

    def _write_repo(self, json_data, repo):
        repo_string = "%s|%s|%s" % (repo[0], repo[1], repo[2])
        json_data["repo"] = repo_string


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
            # Find the last hash commit in the repo
            url = get_repo_url(repo["user_name"], repo["repo_name"])
            args = ["git", "ls-remote", url]

            p = subprocess.Popen(args, stdout=subprocess.PIPE)
            out, err = p.communicate()

            repo_hash = None
            for l in out.split("\n"):
                if (l.endswith("HEAD")):
                    repo_hash = l.replace("HEAD", "").strip()
            if repo_hash == None:
                logging.warning("Commit hash not found for %s, skipping it " % str(repo))
            else:
                print repo_hash
                res.append((repo["user_name"], repo["repo_name"], repo_hash))
    return res


class RepoProcessor:
    """Implements the different phases needed to process the repos
    """

    class BuildInfo:
        def __init__(self, result_record):
            apps_prop = result_record["apps"]

            for (key, value) in apps_prop.iteritems():
                self.apks = []
                for apk in value["apk"]:
                    self.apks.append(apk)

                self.classes = []
                for cls in value["cls"]:
                    self.classes.append(cls)

                self.jars = []
                for jar in value["jar"]:
                    self.jars.append(jar)

                self.src = []
                for src in value["src"]:
                    self.src.append(src)

                # TODO: extend to multiple APPS
                break

    def __init__(self, in_dir,
                 graph_dir, prov_dir,
                 slice_filter,
                 extractor_jar, classpath,
                 buildable_repos_list = None,
                 buildable_repos_path = None,
                 extractor_status=None,
                 tot_workers=1,
                 read_apk=False):
        # Keeps the error log for each repo
        self.log = ErrorLog()
        # Directory where download the repositories
        self.in_dir = in_dir
        self.graph_dir = graph_dir
        self.prov_dir = prov_dir
        self.slice_filter = slice_filter
        self.extractor_jar = extractor_jar
        self.classpath = classpath
        self.tot_workers = tot_workers
        self.read_apk = read_apk

        if extractor_status is None:
            extractor_statis = "extractor_status.json"
        self.extractor_status = ExtractorStatus(extractor_status)

        self.android_home = None
        if 'ANDROID_HOME' not in os.environ:
            raise Exception("ANDROID_HOME path is not set")
        else:
            self.android_home = os.environ['ANDROID_HOME']

        self.built_info = None
        if (buildable_repos_list is not None):
            # map from "user|repo|hash" to built info
            self.built_info = {}
            # read the buildable status
            with open(buildable_repos_list, 'rt') as fbuilt:
                built_data = json.load(fbuilt)

                assert ("results" in built_data)

                for built_repo in built_data["results"]:
                    key = "%s|%s|%s" % (built_repo["user"], built_repo["repo"], built_repo["hash"])
                    build_info = RepoProcessor.BuildInfo(built_repo)
                    self.built_info[key] = build_info
        self.buildable_repos_path = buildable_repos_path


    @staticmethod
    def _call_sub(log, repo, args, cwd=None, wait=True):
        """Call a subprocess.
        """
        write_log(log,repo,"Executing %s" % " ".join(args),"info")

        if log is None:
            #TODO: check if this is still the case
            # not pipe stdout - processes will hang
            # Known limitation of Popen
            proc = subprocess.Popen(args, cwd=cwd)
            proc.wait()
        else:
            proc = subprocess.Popen(args, cwd=cwd,
                                    stdout = subprocess.PIPE,
                                    stderr = subprocess.PIPE,
                                    )
            stdout, stderr = proc.communicate()
            write_log(log,repo,"Graph extractor stdout %s" % stdout,"debug")
            write_log(log,repo,"Graph extractor stderr %s" % stderr, "debug")

        return_code = proc.returncode
        if (return_code != 0):
            err_msg = "Error code is %s\nCommand line is: %s\n%s" % (str(return_code), str(" ".join(args)),"\n")
            write_log(log, repo, err_msg)

            return False

        return True


    def download(self, repo):
        """Dowload the repository."""
        logging.info("Download task for repo (disable download): " + str(repo))
        return repo

        try:
            import pygit2
        except Exception as e:
            logging.error("Error importing pygit2.")
            print "Error importing pygit2."
            self.log.add_error(repo, e.message)
            return None

        repo_url = get_repo_url(repo[0], repo[1])
        repo_folder = get_repo_path(self.in_dir, repo)

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

    def lookup_build(self, repo):
        try:
            key = "%s|%s|%s" % (repo[0], repo[1], repo[2])
            built_info = self.built_info[key]
            logging.debug("Found repo %s in BuilderFarm " % (key))
            return built_info
        except KeyError:
            return None

    def build_from_sources(self, repo):
        """Build the repo.
        """
        logging.debug("Building %s/%s" % (repo[0], repo[1]))

        repo_folder = get_repo_path(self.in_dir, repo)
        assert (os.path.exists(repo_folder))

        (gradle_build_file, gradle_path) = getGradleInfo(repo, repo_folder)
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
            is_ok = RepoProcessor._call_sub(self.log, repo, [compile_cmd, "--stacktrace",
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

    def build(self, repo):
        """ Try to lookup from the repo, and build otherwise """
        build_info = self.lookup_build(repo)
        if build_info is None:
            logging.debug("Skipping repo not built by service!")
            # assert False
            # return self.build_from_sources(repo)
        else:
            return repo

    @staticmethod
    def extract_static(repo,
                       log,
                       in_dir,
                       android_home,
                       graph_dir,
                       prov_dir,
                       classpath,
                       extractor_jar,
                       build_info,
                       buildable_repos_path,
                       file_filter=None):


        """Extract the graph for repo."""
        write_log(log,repo,"Extracting graphs for repo","info")

        if build_info is None:
            write_log(log,repo,"Build information not found...","debug")
            repo_folder = get_repo_path(in_dir, repo)

            app_gradle_file_path = getAndroidAppPlugin(log, repo, repo_folder)
            if None == app_gradle_file_path:
                # Error, classes.jar not found
                msg = "Cannot find application build.gradle file for %s/%s" % (repo[0], repo[1])
                logging.debug(msg)
                write_log(log, repo, msg)
                return None

            app_gradle_file = os.path.join(app_gradle_file_path, "build.gradle")
            write_log(log,repo,"App gradle file is %s" % app_gradle_file,"debug")
            (min_apk, max_apk, version_number) = get_version_from_gradle(app_gradle_file)

            # set the process_dir: we look for the classes.jar file created
            # during the build.
            single_dir = search_classes(repo_folder, app_gradle_file_path)
            if single_dir is None:
                process_dirs = []
            else:
                process_dirs = [single_dir]
        else:
            write_log(log,repo,"Found information...","debug")
            repo_folder = os.path.join("/tmp", "%s.%s.%s" % (repo[0], repo[1], repo[2]))
            version_number = 25

            base_buildable_repo_folder = os.path.join(buildable_repos_path, repo[0], repo[1], repo[2])

            process_dirs = []
            if len(build_info.jars) > 0:
                for jar in build_info.jars:
                    abs_dir = os.path.join(base_buildable_repo_folder,jar)
                    process_dirs.append(abs_dir)
            elif len(build_info.classes) > 0:
                for c in build_info.classes:
                    abs_dir = os.path.join(base_buildable_repo_folder,c)
                    process_dirs.append(abs_dir)

        # get jar file from the android sdk
        android_jar_path = get_android_jar(android_home, version_number)
        if None == android_jar_path:
            msg = "Cannot find the jar for %s/%s" % (repo[0], repo[1])
            write_log(log,repo,msg,"debug")
            write_log(log, repo, msg)
            return None

        if 0 == len(process_dirs):
            # Error, classes.jar not found
            write_log(log,repo,"Cannot find classes.jar","error")
            return None

        # Small try on support libraries
        write_log(log,repo,"Android jar path: %s for %s/%s" % (android_jar_path, repo[0], repo[1]),"debug")

        try:
            repo_graph_dir = get_repo_path(graph_dir, repo)
            if not os.path.isdir(repo_graph_dir): os.makedirs(repo_graph_dir)

            repo_prov_dir = get_repo_path(prov_dir, repo)
            if not os.path.isdir(repo_prov_dir): os.makedirs(repo_prov_dir)

            additional_cp = android_jar_path

            def get_class_path(full_classes_path):
                class_path = []
                for p in full_classes_path.split("/"):
                    class_path.append(p)
                    # print p
                    if p == "classes":
                        break
                return "/".join(class_path)
            process_dirs_paths = set()
            for pd in process_dirs:
                process_dirs_paths.add(get_class_path(pd))
            process_dirs = process_dirs_paths
            for pd in process_dirs:
                additional_cp = additional_cp + ":" + pd

            if classpath != None:
                classpath = classpath + ":" + additional_cp
            else:
                classpath = additional_cp

            repo_url = get_repo_url(repo[0], repo[1])
            # args = ["runlim",
            #         "--time-limit=1200",
            #         "java",
            #         "-Xms%s" % MIN_HEAP_SIZE,
            #         "-Xmx%s" % MAX_HEAP_SIZE,
            #         "-jar", extractor_jar,
            #         "-s", "false", # we read bytecode
            #         "-l", classpath,
            #         "-o", repo_graph_dir,
            #         "-d", repo_prov_dir,
            #         "-j", "true", # enable jphantom
            #         "-z", repo_folder,
            #         "-t", TIMEOUT,
            #         "-n", repo[0],
            #         "-r", repo[1],
            #         "-u", repo_url]

            args = ["java",
                    "-Xms%s" % MIN_HEAP_SIZE,
                    "-Xmx%s" % MAX_HEAP_SIZE,
                    "-jar", extractor_jar,
                    "-s", "false", # we read bytecode
                    "-l", classpath,
                    "-o", repo_graph_dir,
                    "-d", repo_prov_dir,
                    "-j", "true", # enable jphantom
                    "-z", repo_folder,
                    "-t", TIMEOUT,
                    "-n", repo[0],
                    "-r", repo[1],
                    "-u", repo_url]

            if file_filter is not None:
                args.append("-q")
                if isinstance(file_filter, str):
                    args.append(file_filter)
                elif isinstance(file_filter, list):
                    args.append(":".join(file_filter))

            args.append("-p")

            # remove google support libraries from the thing to
            # process
            new_process_dirs = []
            ignore = ["/com.google.android.", "/com.android.",
                      "/android.","/androidx."]
            for p in process_dirs:
                for i in ignore:
                   if i in p:
                       continue
                new_process_dirs.append(p)
            args.append(":".join(new_process_dirs))

            if len(repo) > 2:
                args.append("-h")
                args.append(repo[2])

            is_ok = RepoProcessor._call_sub(log, repo, args)
            if not is_ok:
                msg = "call_sub ended in error for %s/%s" % (repo[0], repo[1])
                write_log(log, repo, msg)
                return None

        except Exception as e:
            traceback.print_exc()

            write_log(log,repo,"Cannot extract the graphs from %s/%s/%s" % (repo[0], repo[1], repo[2]),"debug")
            write_log(log, repo, e.message)
            return None

        write_log(log,repo,"Extraction of graph ended for %s/%s/%s" % (repo[0], repo[1],repo[2]),"debug")
        return repo

    @staticmethod
    def extract_static_apk(repo,
                           log,
                           android_home,
                           graph_dir,
                           prov_dir,
                           extractor_jar,
                           build_info,
                           buildable_repos_path):
        """Extract the graph for repo."""
        logging.info("Extracting graphs for repo: " + str(repo))

        assert (not build_info is None)
        
        # Base path to the repo
        base_buildable_repo_folder = os.path.join(buildable_repos_path,
                                                  repo[0],
                                                  repo[1],
                                                  repo[2])
        # Pick one apk
        if (len(build_info.apks) < 1):
            msg = "No apk files for %s/%s" % (repo[0], repo[1])
            logging.debug(msg)
            write_log(log, repo, msg)
            return None

        apk_rel_path = build_info.apks[0]
        apk_full_path = os.path.join(base_buildable_repo_folder, apk_rel_path)
        if (not os.path.exists(apk_full_path)):
            msg = "Cannot find apk file for %s/%s" % (repo[0], repo[1])
            logging.debug(msg)
            write_log(log, repo, msg)
            return None

        platforms_path = os.path.join(os.path.abspath(android_home), "platforms")
        if (not os.path.isdir(platforms_path)):
            msg = "Cannot find the Android platforms in %s for %s/%s" % (platforms_path,
                                                                         repo[0],
                                                                         repo[1])
            logging.debug(msg)
            write_log(log, repo, msg)
            return None

        # Compose and run the command
        try:
            repo_graph_dir = get_repo_path(graph_dir, repo)
            if not os.path.isdir(repo_graph_dir): os.makedirs(repo_graph_dir)

            repo_prov_dir = get_repo_path(prov_dir, repo)
            if not os.path.isdir(repo_prov_dir): os.makedirs(repo_prov_dir)

            tmp_folder = os.path.join("/tmp", "%s.%s.%s" % (repo[0], repo[1], repo[2]))

            repo_url = get_repo_url(repo[0], repo[1])

            args = ["java",
                    "-Xms%s" % MIN_HEAP_SIZE,
                    "-Xmx%s" % MAX_HEAP_SIZE,
                    "-jar", extractor_jar,
                    "-a", "true", # we read the apk
                    "-s", "false",  # we read bytecode
                    "-l", os.path.dirname(apk_full_path),
                    "-o", repo_graph_dir,
                    "-d", repo_prov_dir,
                    "-j", "true", # enable jphantom
                    "-z", tmp_folder,
                    "-t", TIMEOUT,
                    "-n", repo[0],
                    "-r", repo[1],
                    "-u", repo_url,
                    "-p", apk_full_path,
                    "-w", platforms_path]

            if len(repo) > 2:
                args.append("-h")
                args.append(repo[2])

            is_ok = RepoProcessor._call_sub(log, repo, args)
            if not is_ok:
                msg = "call_sub ended in error for %s/%s" % (repo[0], repo[1])
                logging.debug(msg)
                write_log(log, repo, msg)
                return None

        except Exception as e:
            traceback.print_exc()

            logging.debug("Cannot extract the graphs from %s/%s/%s" % (repo[0], repo[1], repo[2]))
            write_log(log, repo, e.message)
            return None

        logging.debug("Extraction of graph ended for %s/%s/%s" % (repo[0], repo[1],repo[2]))
        return repo            


    def extract(self, repo):

        log = self.log
        android_home = self.android_home
        graph_dir = self.graph_dir
        prov_dir = self.prov_dir
        extractor_jar = self.extractor_jar
        build_info = self.lookup_build(repo)
        buildable_repos_path = self.buildable_repos_path
        if (not self.read_apk):
            return RepoProcessor.extract_static(repo,
                                                log,
                                                self.in_dir,
                                                android_home,
                                                graph_dir,
                                                prov_dir,
                                                self.classpath,
                                                extractor_jar,
                                                build_info,
                                                buildable_repos_path)
        else:
            return RepoProcessor.extract_static_apk(repo,
                                                    log,
                                                    android_home,
                                                    graph_dir,
                                                    prov_dir,
                                                    extractor_jar,
                                                    build_info,
                                                    buildable_repos_path)


    def processRepoFromStep(self, repo, task_index):
        tasks = {"download": self.download,
                 "build": self.build,
                 "extract" : self.extract}

        steps_to_do = ExtractorStatus.tasks_list[task_index:]

        # read the status of the repo
        repo_status = self.extractor_status.get_status(repo)

        if repo_status < MIN_STATUS:
            logging.warning("Skipping repo %s (repo status %d < min status %d" %
                            (get_repo_name(repo), repo_status,
                             MIN_STATUS))
            return

        repo_step_list = []
        found_status = False
        currentTask = ExtractorStatus.status2task[repo_status]
        for l in steps_to_do:
            if l == currentTask:
                found_status = True
            if found_status and l != "done":
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
                self.extractor_status.next_status(repo)
            self.extractor_status.write()

    @staticmethod
    def workerfun(tasks_queue):
        while True:
            data = tasks_queue.get()
            if data is None:
                break

            (repoProcessor, repo, task_index, repo_index, tot_repos) = data
            logging.info("Repo %d/%d..." % (repo_index, tot_repos))
            logging.info("Repo %s" % get_repo_name(repo))

            try:
                repoProcessor.processRepoFromStep(repo, task_index)
            except Exception:
                traceback.print_exc()

                logging.error("Thread: error processing repo " \
                              "%d/%d" % (repo_index, tot_repos))
                logging.error("Thread: error processing repo " \
                              "%s" % (get_repo_name(repo)))

            finally:
                tasks_queue.task_done()

    def processFromStep(self, repo_list, user_task):
        assert (user_task in ExtractorStatus.task2status.keys())
        assert (user_task in ExtractorStatus.tasks_list)

        task_index = ExtractorStatus.tasks_list.index(user_task)
        steps_to_do = ExtractorStatus.tasks_list[task_index:]

        # Creates the worker threads
        tasks_queue = Queue.Queue()
        threads = []
        workerpart = functools.partial(RepoProcessor.workerfun, tasks_queue)

        for i in range(self.tot_workers):
            t = threading.Thread(target=workerpart)
            t.start()
            threads.append(t)

        repo_index = 0
        tot_repos = len(repo_list)
        processed = set()
        for repo in repo_list:
            repo_index = repo_index + 1

            if repo in processed:
                logging.info("Repo %d/%d already processed" % (repo_index, tot_repos))
                logging.info("Repo %s already processed" % get_repo_name(repo))
            else:
                worker_data = (self, repo, task_index, repo_index, tot_repos)
                tasks_queue.put(worker_data)
                processed.add(repo)
            repo_index = repo_index + 1

        # block until all tasks are done
        tasks_queue.join()

        # stop workers
        for i in range(self.tot_workers):
            tasks_queue.put(None)
        for t in threads:
            t.join()

    def printErrors(self, out):
        self.log.printErrors(out)


    @staticmethod
    def init_extraction(indir, graphdir, provdir, applist):
        # create the indir, graphdir and provdir if they do not exist
        new_dir = [indir,graphdir,provdir]
        for d in new_dir:
            if not os.path.isdir(d):
                os.mkdir(d)

        # read the list of repositories
        with open(applist, 'r') as app_list_file:
            repo_list = read_repo(app_list_file)
        return repo_list

    @staticmethod
    def get_out_paths(output_dir):
        indir = os.path.join(output_dir, "src_repo")
        graphdir  = os.path.join(output_dir, "graphs")
        provdir = os.path.join(output_dir, "provenance")
        return (indir, graphdir, provdir)
        

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

    p.add_option('-b', '--buildable_repos_list', help="JSON file containing the list of all the buildable repos")
    p.add_option('-r', '--buildable_repos_path', help="Path to the buildable repos")
    p.add_option('-o', '--extractor_status', help="Extractor status")

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
    required = [opts.applist, opts.indir, opts.graphdir, opts.step, opts.extractor_status]
    required_desc = ["--applist", "--indir", "--graphdir", "--step", "--extractor_status"]
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

    if (opts.buildable_repos_list or opts.buildable_repos_path):
        if (not opts.buildable_repos_list): usage("Missing JSON file with buildable info")
        if (not opts.buildable_repos_path): usage("Missing PATH to buildable files")

        if (not os.path.exists(opts.buildable_repos_list)): usage("%s  does not exist" % opts.buildable_repos_list)
        if (not os.path.isdir(opts.buildable_repos_path)): usage("%s  does not exist" % opts.buildable_repos_path)

        buildable_repos_list = opts.buildable_repos_list
        buildable_repos_path = opts.buildable_repos_path
    else:
        buildable_repos_list = None
        buildable_repos_path = None

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
        repo_list = RepoProcessor.init_extraction(opts.indir,
                                                  opts.graphdir,
                                                  opts.provdir,
                                                  opts.applist)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)


    extractor_status = os.path.join(opts.graphdir,opts.extractor_status)
    # process the repos
    repoProcessor = RepoProcessor(opts.indir, opts.graphdir,
                                  opts.provdir,
                                  opts.filter,
                                  opts.extractorjar, opts.classpath,
                                  buildable_repos_list,
                                  buildable_repos_path,
                                  extractor_status)
    repoProcessor.processFromStep(repo_list, opts.step)

    # DO NOT PRINT THE ERROR LOG FOR EACH REPO
    # try:
    #     for repo in repo_list:
    #         if repoProcessor.log.hasError(repo):
    #             assert (len(repo) == 3)
    #             repo_name = str(repo[0] + "_" + repo[1])
    #             repo_name = repo_name.replace("/", "_")
    #             commit_hash = repo[2]

    #             logfile = "repo_log_%s_%s.log" % (repo_name, commit_hash)


    #             with open(logfile , 'w') as out_file:
    #                 repoProcessor.log.printErrorRepo(repo, out_file)
    #                 out_file.flush()
    #                 out_file.close()

    # except Exception as e:
    #     traceback.print_exc()
    #     sys.exit(1)


if __name__ == '__main__':
    log_name = "extraction_log_" + str(os.getpid())
    logging.basicConfig(filename = log_name, level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)

    file_to_check = []
    for f in file_to_check:
        logging.info("Searching for file %s" % f)
        assert(os.path.isfile(f))

    main()

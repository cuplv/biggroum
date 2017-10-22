# APIs used to perform the extraction of the ACDFGs (or groums)
#
# The class AppBuilderAPI allows to lookup the built artifacts for a repository
#
# The class RepoProcessor provides the functionalities to:
#   1. Process a github repository and generate the ACDFGs.
#     - the input is a github repository, an API to the Fixr builder data, and the output path to the results.
#     - the outputs are:
#       - a status code
#       - the graphs and provenance information created from the repository
#     This step run the graph extractor on the APKs or classes found in the repository.
#
#   2. Process a list of repositories extracting the graphs, keeping track of the status of the extraction
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
import collections
from xml.dom.minidom import parse, parseString


# RepoVersion = collections.namedtuple('RepoVersion', 'user_name repo_name hash_str')

class GitUtils:
    @staticmethod
    def get_key(user_name, repo_name, hash_str):
        """ Generate a key for a repo """
        key = "%s|%s|%s" % (user_name, repo_name, hash_str)
        return key


class AppBuilderAPI:
    """ API used to query the archive of built github projects """

    class BuildInfo:
        """ Store the information of the build info """
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

                # exit at the first app found in the APK
                break

        def get_apk(self):
            raise NotImplemented


    def __init__(self, info_json, data_path):
        """ info_json: the file that contains the information on the built repositories
            data_path: path to the artifacts produced in the build
        """
        self.info_json = info_json
        self.data_path = data_path

        # Build an index of the built information
        # Map from "user|repo|hash" to built info
        self.build_info = AppBuilderAPI.get_build_info(self.info_json)

        
    @staticmethod
    def get_build_info(info_json):
        assert (info_json is not None)
        # map from "user|repo|hash" to built info
        built_info = {}

        # read the buildable json file
        with open(info_json, 'rt') as fbuilt:
            built_data = json.load(fbuilt)
            assert ("results" in built_data)

            for built_repo in built_data["results"]:
                key = GitUtils.get_key(built_repo["user"], built_repo["repo"], built_repo["hash"])
                repo_info = AppBuilderAPI.BuildInfo(built_repo)
                built_info[key] = repo_info

        return built_info

    def lookup_build_info(self, user_name, repo_name, hash_str):
        """ Lookup the build info record for the repository.

        Returns None if the repo record is not in the built apps.
        """
        key = GitUtils.get_key(user_name, repo_name, hash_str)

        try:
            built_info = self.build_info[key]
            return built_info
        except KeyError:
            return None


class RepoProcessor:
    
    @staticmethod
    def extract_graph_from_repo_version():
        raise NotImplementedError

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
                       buildable_repos_path):
        """ Extract all the graphs from the APK """

        logging.info("Extracting graphs for repo: " + str(repo))


        # get jar file from the android sdk
        android_jar_path = RepoProcessor.get_android_jar(android_home, version_number)
        if None == android_jar_path:
            msg = "Cannot find the jar for %s/%s" % (repo[0], repo[1])
            logging.debug(msg)
            RepoProcessor.write_log(log, repo, msg)
            return None

        if 0 == len(process_dirs):
            # Error, classes.jar not found
            logging.debug("Cannot find classes.jar for %s/%s" % (repo[0], repo[1]))
            RepoProcessor.write_log(log, repo, "Cannot find classes.jar for %s/%s" % (repo[0], repo[1]))
            return None

        # Small try on support libraries
        logging.debug("Android jar path: %s for %s/%s" % (android_jar_path, repo[0], repo[1]))

        try:
            repo_graph_dir = RepoProcessor.get_repo_path(graph_dir, repo)
            if not os.path.isdir(repo_graph_dir): os.makedirs(repo_graph_dir)

            repo_prov_dir = RepoProcessor.get_repo_path(prov_dir, repo)
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

            repo_url = RepoProcessor.get_repo_url(repo[0], repo[1])
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


            args.append("-p")

            # remove google support libraries from the thing to
            # process
            new_process_dirs = []
            ignore = ["/com.google.android.", "/com.android.",
                      "/android."]
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
                logging.debug(msg)
                RepoProcessor.write_log(log, repo, msg)
                return None

        except Exception as e:
            traceback.print_exc()

            # DEBUG
            logging.debug("Cannot extract the graphs from %s/%s/%s" % (repo[0], repo[1], repo[2]))
            RepoProcessor.write_log(log, repo, e.message)
            return None

        logging.debug("Extraction of graph ended for %s/%s/%s" % (repo[0], repo[1],repo[2]))
        return repo



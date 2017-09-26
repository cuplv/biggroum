# APIs used to perform the extraction of the ACDFGs (or groums)
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


#class RepoProcessor:
#            logging.debug("Found repo %s in BuilderFarm " % (key))


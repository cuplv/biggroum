import random
import shutil
import logging
import unittest
import sys
import os
import tempfile
from fixrgraph.extraction import extract_single

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class TestExtractSingle(unittest.TestCase):
    EXTRACTOR_JAR="../../../FixrGraphExtractor/target/scala-2.12/fixrgraphextractor_2.12-0.1.0-one-jar.jar"
    BUILT_APP_TEST = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  "test_data/built_app_directories/AwesomeApp")
    HASH="9d759f47dc6b7b404a32eafcbc654b134bf6778a"
    def test_class_file_extraction(self):
        try:
            graphdir = tempfile.mkdtemp(".groum_test_extract_single")
            extract_single.extract_single_class_dir(repo = ["cuplv","AwesomeApp",self.HASH],
                                                    out_dir=graphdir,
                                                    extractor_jar=self.EXTRACTOR_JAR,
                                                    path = self.BUILT_APP_TEST)
            topdir = os.listdir(graphdir)
            assert("repo_graph_dir" in topdir)
            repo_graph_dir = os.listdir(os.sep.join([graphdir,"repo_graph_dir","cuplv","AwesomeApp",self.HASH]))

            assert(len(repo_graph_dir) > 0)

        finally:
            shutil.rmtree(graphdir)
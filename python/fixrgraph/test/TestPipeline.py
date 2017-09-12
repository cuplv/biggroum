""" Test the glue code

 """

from fixrgraph.pipeline import Pipeline

import logging
import unittest
import sys
import os

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestPipeLine(unittest.TestCase):

    def test_graph_extraction(self):
        test_data_path = os.path.join(os.path.dirname(fixrgraph.test.__file__), "test_data")

        repo_list = os.path.join(test_data_path, "repo_list.json")
        buildable_list = os.path.join(test_data_path, "buildable_small.json")
        build_data = os.path.join(test_data_path, "build-data")
        out_path = os.path.join(test_data_path, "output")

        config = Pipeline.ExtractConfig("/Users/sergiomover/works/projects/muse/repos/FixrGraphExtractor/target/scala-2.11/fixrgraphextractor_2.11-0.1-SNAPSHOT-one-jar.jar",
                                        repo_list, buildable_list, build_data, out_path)
        # TODO: check results
        Pipeline.extractGraphs(config)


        # TODO: cleanup 




        

import shutil
import os
import tempfile
from fixrgraph.extraction import extract_single
from fixrgraph.test.test_pipeline import TestPipeline
import fixrgraph.test

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class TestExtractSingle(unittest.TestCase):

    def test_class_file_extraction(self):
        extractor_path = TestPipeline.get_extractor_path()

        test_path = os.path.abspath(os.path.dirname(fixrgraph.test.__file__))
        test_data_path = os.path.join(test_path, "test_data")

        build_app_test = os.path.join(os.path.dirname(fixrgraph.test.__file__),
                                      test_data_path,
                                      "built_app_directories/AwesomeApp")
        app_hash = "9d759f47dc6b7b404a32eafcbc654b134bf6778a"

        graphdir = None
        try:
            graphdir = tempfile.mkdtemp(prefix="groum_test_extract_single",
                                        dir=test_data_path)

            extract_single.extract_single_class_dir(repo = ["cuplv", "AwesomeApp", app_hash],
                                                    out_dir = graphdir,
                                                    extractor_jar = extractor_path,
                                                    path = build_app_test)

            self.assertTrue("graphs" in os.listdir(graphdir))
            repo_graph_dir = os.listdir(os.sep.join([graphdir, "graphs", "cuplv", "AwesomeApp", app_hash]))

            self.assertTrue(len(repo_graph_dir) > 0)

        finally:
            if graphdir is not None:
                if os.path.isdir(graphdir):
                    shutil.rmtree(graphdir)

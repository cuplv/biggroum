""" Test the glue code

 """

from fixrgraph.pipeline.pipeline import Pipeline
import fixrgraph

import shutil
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
        test_path = os.path.abspath(os.path.dirname(fixrgraph.test.__file__))
        test_data_path = os.path.join(test_path, "test_data")

        extractor_path = os.path.join(test_path, os.pardir)
        extractor_path = os.path.join(extractor_path, os.pardir)
        extractor_path = os.path.join(extractor_path, os.pardir)
        extractor_path = os.path.join(extractor_path, os.pardir)
        extractor_path = os.path.abspath(extractor_path)
        extractor_path = os.path.join(extractor_path,
                                      "FixrGraphExtractor/target/scala-2.11/fixrgraphextractor_2.11-0.1-SNAPSHOT-one-jar.jar")

        repo_list = os.path.join(test_data_path, "repo_list.json")
        buildable_list = os.path.join(test_data_path, "buildable_small.json")
        build_data = os.path.join(test_data_path, "build-data")
        out_path = os.path.join(test_data_path, "output")

        fixrgraph_jar = os.path.join(test_data_path, "repo_list.json")

        config = Pipeline.ExtractConfig(extractor_path,
                                        repo_list, buildable_list, build_data, out_path)
        Pipeline.extractGraphs(config)

        # some files that must have been created by running the test
        created_files = ["graphs/learning-android/Yamba/46795d3c4a1f56416f88a18b708d9db36a429025/com.marakana.android.yamba.YambaWidget_onReceive.acdfg.bin",
                        "provenance/learning-android/Yamba/46795d3c4a1f56416f88a18b708d9db36a429025/com.marakana.android.yamba.YambaWidget_onReceive.acdfg.dot",
                         "provenance/learning-android/Yamba/46795d3c4a1f56416f88a18b708d9db36a429025/com.marakana.android.yamba.YambaWidget_onReceive.cdfg.dot",
                         "provenance/learning-android/Yamba/46795d3c4a1f56416f88a18b708d9db36a429025/com.marakana.android.yamba.YambaWidget_onReceive.cfg.dot",
                         "provenance/learning-android/Yamba/46795d3c4a1f56416f88a18b708d9db36a429025/com.marakana.android.yamba.YambaWidget_onReceive.html",
                         "provenance/learning-android/Yamba/46795d3c4a1f56416f88a18b708d9db36a429025/com.marakana.android.yamba.YambaWidget_onReceive.jimple",
                         "provenance/learning-android/Yamba/46795d3c4a1f56416f88a18b708d9db36a429025/com.marakana.android.yamba.YambaWidget_onReceive.sliced.jimple"]

        for f in created_files:
            f_path = os.path.join(os.path.join(test_data_path, out_path), f)
            self.assertTrue(os.path.exists(f_path))
                         
        # cleanup 
        if os.path.exists(out_path):
            shutil.rmtree(out_path)




        

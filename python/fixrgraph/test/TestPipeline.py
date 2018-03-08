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


class TestPipeline(unittest.TestCase):

    @staticmethod
    def get_repo_path():
        test_path = os.path.abspath(os.path.dirname(fixrgraph.test.__file__))
        repo_path = os.path.join(test_path, os.pardir)
        repo_path = os.path.join(repo_path, os.pardir)
        repo_path = os.path.join(repo_path, os.pardir)
        repo_path = os.path.abspath(repo_path)

        return repo_path

    @staticmethod
    def get_extractor_path():
        repo_path = TestPipeline.get_repo_path()
        extractor_path = os.path.join(repo_path,
                                      "FixrGraphExtractor/target/scala-2.11/fixrgraphextractor_2.11-0.1-SNAPSHOT-one-jar.jar")
        return extractor_path

    @staticmethod
    def get_fixrgraphiso_path():
        # Set the path of the itemset computator
        repo_path = TestPipeline.get_repo_path()
        fixrgraphiso_path = os.path.join(repo_path,
                                         "FixrGraphIso/build/src/fixrgraphiso/frequentitemsets")
        return fixrgraphiso_path

    @staticmethod
    def get_frequentsubgraphs_path():
        repo_path = TestPipeline.get_repo_path()
        frequentsubgraphs_path = os.path.join(repo_path,
                                              "FixrGraphIso",
                                              "build",
                                              "src",
                                              "fixrgraphiso",
                                              "frequentsubgraphs")
        return frequentsubgraphs_path

    @staticmethod
    def get_gather_results_path():
        repo_path = TestPipeline.get_repo_path()
        gather_results_path = os.path.join(repo_path,
                                           "FixrGraphIso",
                                           "scripts",
                                           "gatherResults.py")
        return gather_results_path


    def test_graph_extraction(self):
        test_path = os.path.abspath(os.path.dirname(fixrgraph.test.__file__))
        test_data_path = os.path.join(test_path, "test_data")

        extractor_path = TestPipeline.get_extractor_path()

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


    def test_itemset_computation(self):
        # Set the paths
        test_path = os.path.abspath(os.path.dirname(fixrgraph.test.__file__))
        test_data_path = os.path.join(test_path, "test_data")
        groums_path = os.path.join(test_data_path, "groums")

        # Set the path of the itemset computator
        fixrgraphiso_path = TestPipeline.get_fixrgraphiso_path()

        cluster_path = os.path.join(test_data_path, "clusters")
        os.mkdir(cluster_path)
        cluster_file_path = os.path.join(cluster_path, "clusters.txt")

        # get list of groums
        groum_files_path = os.path.join(cluster_path, "groums_list.txt")
        groums_list = []
        for fname in os.listdir(groums_path):
            if fname.endswith(".bin"):
                groums_list.append(os.path.join(groums_path, fname))
        with open(groum_files_path, "w") as gfile:
            for g in groums_list:
                gfile.write("%s\n" % g)
        gfile.close()        

        config = Pipeline.ItemsetCompConfig(fixrgraphiso_path,
                                            2,
                                            1,
                                            groum_files_path,
                                            cluster_path,
                                            cluster_file_path)
        Pipeline.computeItemsets(config)

        # Check the itemset computation
        self.assertTrue(config.cluster_file)
        cf = open(cluster_file_path, 'r')
        cf_lines = cf.readlines()
        self.assertTrue(cf_lines[0].startswith("I:"))
        for i in range(6):
            self.assertTrue(cf_lines[i+1].startswith("F:"))
        self.assertTrue(cf_lines[7].startswith("E"))

        # Check the creation of the cluster folders
        acdfg_link = os.path.join(config.cluster_path,
                                  "all_clusters",
                                  "cluster_1",
                                  "tv.acfun.a63.DonateActivity_showErrorDialog.acdfg.bin")
        self.assertTrue(os.path.exists(acdfg_link))

        methods_file = os.path.join(config.cluster_path,
                                    "all_clusters",
                                    "cluster_1",
                                    "methods_1.txt")
        self.assertTrue(os.path.exists(methods_file))

        # cleanup 
        if os.path.exists(cluster_path):
            shutil.rmtree(cluster_path)


    def test_pattern_computation(self):
        # Set the paths
        test_path = os.path.abspath(os.path.dirname(fixrgraph.test.__file__))
        test_data_path = os.path.join(test_path, "test_data")
        groums_path = os.path.join(test_data_path, "groums")

        # Set the path of the itemset computator
        frequentsubgraphs_path = TestPipeline.get_frequentsubgraphs_path()
        cluster_path = os.path.join(test_data_path, "clusters_data")
        cluster_file_path = os.path.join(cluster_path, "clusters.txt")

        config = Pipeline.ComputePatternsConfig(groums_path,
                                                cluster_path,
                                                cluster_file_path,
                                                10,
                                                2,
                                                frequentsubgraphs_path)

        Pipeline.computePatterns(config)

        cluster_1_path = os.path.join(cluster_path, "all_clusters", "cluster_1")
        created = [os.path.join(cluster_path, "makefile"),
                   os.path.join(cluster_1_path, "run1.err.out"),
                   os.path.join(cluster_1_path, "run1.out"),
                   os.path.join(cluster_1_path, "cluster_1_info.txt"),
                   os.path.join(cluster_1_path, "pop_1.acdfg.bin"),
                   os.path.join(cluster_1_path, "pop_2.acdfg.bin"),
                   os.path.join(cluster_1_path, "anom_1.acdfg.bin"),
                   os.path.join(cluster_1_path, "pop_1.dot"),
                   os.path.join(cluster_1_path, "pop_2.dot"),
                   os.path.join(cluster_1_path, "anom_1.dot")]

        for c in created:
            self.assertTrue(os.path.exists(c))
            # cleanup
            os.remove(c)


    def test_create_html(self):
        # Set the paths
        test_path = os.path.abspath(os.path.dirname(fixrgraph.test.__file__))
        test_data_path = os.path.join(test_path, "test_data")

        # Set the path of the html creator
        gather_results_path = TestPipeline.get_gather_results_path()
        cluster_path = os.path.join(test_data_path, "clusters_data_html")
        html_path = os.path.join(cluster_path, "html_files")

        config = Pipeline.ComputeHtmlConfig(cluster_path,
                                            "1",
                                            gather_results_path)

        Pipeline.computeHtml(config)

        created = ["cluster_1.html",
                   "cluster_1_anom_1.dot",
                   "cluster_1_pop_1.dot",
                   "cluster_1_pop_2.dot",
                   "index.html"]
        created = [os.path.join(html_path, s) for s in created]
        for c in created:
            self.assertTrue(os.path.exists(c))
            os.remove(c)
        shutil.rmtree(html_path)


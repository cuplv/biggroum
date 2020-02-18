""" Test the glue code

 """

from fixrgraph.pipeline.pipeline import Pipeline
import fixrgraph

import random
import shutil
import logging
import unittest
import sys
import os

try:
    import unittest2 as unittest
except ImportError:
    import unittest


DELETE_FILES = True

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
                                      "FixrGraphExtractor/target/scala-2.12/fixrgraphextractor_2.12-0.1.0-one-jar.jar")
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
    def get_findduplicates_path():
        repo_path = TestPipeline.get_repo_path()
        findduplicates_path = os.path.join(repo_path,
                                              "FixrGraphIso",
                                              "build",
                                              "src",
                                              "fixrgraphiso",
                                              "findDuplicates")
        return findduplicates_path


    @staticmethod
    def get_gather_results_path():
        repo_path = TestPipeline.get_repo_path()
        gather_results_path = os.path.join(repo_path,
                                           "FixrGraphIso",
                                           "scripts",
                                           "gatherResults.py")
        return gather_results_path

    @staticmethod
    def create_groums_file(groums_path, groum_files_path, limit=None):
        # Removes "duplicate" files (same package, class, method name)
        existing_files = set()

        groums_list = []
        duplicates = 0
        for root, subFolder, files in os.walk(groums_path):
            for item in files:
                if item.endswith(".bin") :
                    file_name_path = str(os.path.join(root,item))

                    # Workaround
                    acdfg_simple_name = os.path.basename(file_name_path)
                    acdfg_simple_name = acdfg_simple_name.strip()
                    acdfg_simple_name = acdfg_simple_name.lower()

                    if not acdfg_simple_name in existing_files:
                        groums_list.append(file_name_path)
                        existing_files.add(acdfg_simple_name)
                    else:
                        duplicates = duplicates + 1


        print "Skipping %d duplicates" % duplicates
        if not limit is None:
            groums_list = random.sample(groums_list, limit)

        with open(groum_files_path, "w") as gfile:
            for g in groums_list:
                gfile.write("%s\n" % g)
        gfile.close()


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
                                        repo_list, buildable_list,
                                        build_data, out_path, 1,
                                        False)
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
        if DELETE_FILES and os.path.exists(out_path):
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
        TestPipeline.create_groums_file(groums_path, groum_files_path)

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

        if DELETE_FILES and os.path.exists(cluster_path):
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

        configs = [Pipeline.ComputePatternsConfig(groums_path,
                                                  cluster_path,
                                                  cluster_file_path,
                                                  10,
                                                  2,
                                                  frequentsubgraphs_path),
                   Pipeline.ComputePatternsConfig(groums_path,
                                                  cluster_path,
                                                  cluster_file_path,
                                                  10,
                                                  2,
                                                  frequentsubgraphs_path,
                                                  True,
                                                  0.1)]

        cluster_1_path = os.path.join(cluster_path, "all_clusters", "cluster_1")
        created = [os.path.join(cluster_path, "makefile"),
                   os.path.join(cluster_1_path, "run1.err.out"),
                   os.path.join(cluster_1_path, "run1.out"),
                   os.path.join(cluster_1_path, "cluster_1_info.txt"),
                   os.path.join(cluster_1_path, "cluster_1_lattice.bin"),
                   os.path.join(cluster_1_path, "pop_1.dot"),
                   os.path.join(cluster_1_path, "pop_2.dot"),
                   os.path.join(cluster_1_path, "all_acdfg_bin.txt")]

        results = [[os.path.join(cluster_1_path, "anom_1.dot")] + created,
                   [os.path.join(cluster_1_path, "pop_3.dot"),
                   os.path.join(cluster_1_path, "pop_4.dot"),
                   os.path.join(cluster_1_path, "pop_5.dot")] + created]

        for config, res in zip(configs, results):
            Pipeline.computePatterns(config)

            for c in res:
                logging.debug("Checking creation of %s..." % c)
                self.assertTrue(os.path.exists(c))
                # cleanup
                if DELETE_FILES:
                    print("Removing... %s" % c)
                    os.remove(c)

    def test_compute_duplicates(self):
        # Set the paths
        test_path = os.path.abspath(os.path.dirname(fixrgraph.test.__file__))
        test_data_path = os.path.join(test_path, "test_data")
        cluster_path = os.path.join(test_data_path,
                                    "clusters_data_duplicates")
        duplicates_path = TestPipeline.get_findduplicates_path()
        self.assertTrue(os.path.exists(duplicates_path))

        config  = Pipeline.ComputeDuplicatesConfig(cluster_path, "2",
                                                   duplicates_path)
        Pipeline.computeDuplicates(config)

        lattice_list_file = os.path.join(config.cluster_path,
                                         Pipeline.LATTICE_LIST)
        pattern_duplicate_file = os.path.join(config.cluster_path,
                                              Pipeline.PATTERN_DUPLICATES)
        created = [lattice_list_file, pattern_duplicate_file]

        self.assertTrue(os.path.exists(lattice_list_file))
        self.assertTrue(len(open(lattice_list_file).readlines()) == 2)

        results = ["1,2,2,2","1,3,2,3"]
        for (e, l) in zip(results, open(pattern_duplicate_file).readlines()):
            e = e.strip()
            l = l.strip()
            self.assertTrue(e == l)

        for c in created:
            self.assertTrue(os.path.exists(c))
            if DELETE_FILES:
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
                   "index.html",
                   os.path.join("cluster_1","0.dot"),
                   os.path.join("cluster_1","1.dot"),
                   os.path.join("cluster_1","2.dot"),
                   os.path.join("cluster_1","3.dot"),
                   os.path.join("cluster_1","4.dot"),
                   os.path.join("cluster_1","out.dot")]

        created = [os.path.join(html_path, s) for s in created]

        for c in created:
            self.assertTrue(os.path.exists(c))
            if DELETE_FILES:
                os.remove(c)
        if DELETE_FILES:
            shutil.rmtree(html_path)


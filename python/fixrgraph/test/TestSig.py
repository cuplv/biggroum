""" Test the glue code

 """

import fixrgraph
from fixrgraph.stat_sig.feat import (FeatExtractor, Feat)
from fixrgraph.stat_sig.db import FeatDb
from fixrgraph.stat_sig.extract import process_graphs
from fixrgraph.stat_sig.pvalue import compute_p_value

from fixrgraph.annotator.protobuf.proto_acdfg_pb2 import Acdfg

import shutil
import logging
import unittest
import sys
import os



try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestSig(unittest.TestCase):

    ADDRESS = "localhost"
    USER = "groum"
    PASSWORD = "groum"
    DBNAME = "test_groum_features"

    GRAPH_PATH = "test_data/groums/tv.acfun.a63.MainActivity_showLastPublicReleaseAlert.acdfg.bin"
    ALL_GRAPH_PATH = "test_data/groums"

    def clean_db(self):
        featDb = FeatDb(TestSig.ADDRESS,
                        TestSig.USER,
                        TestSig.PASSWORD,
                        TestSig.DBNAME)
        featDb.open()
        featDb._clean_db()
        featDb.close()

    def _load_graph(self):
        test_path = os.path.abspath(os.path.dirname(fixrgraph.test.__file__))
        file_path = os.path.join(test_path, TestSig.GRAPH_PATH)
        featExtractor = FeatExtractor(file_path)
        return featExtractor

    def test_feature_extraction(self):
        featExtractor = self._load_graph()

        graph_sig = featExtractor.get_graph_sig()
        self.assertTrue(graph_sig == "yromAcFun-Area63https://github.com/yrom/AcFun-Area63403a5f553cff913c51373e48a84880583f89483btv.acfun.a63tv.acfun.a63.MainActivityshowLastPublicReleaseAlertshowLastPublicReleaseAlert")

        features = ["0_1_android.app.AlertDialog$Builder.show_0",
                    "1_1_android.content.SharedPreferences.edit_0",
                    "1_1_android.app.AlertDialog$Builder.setMessage_1",
                    "0_1_android.app.AlertDialog$Builder.<init>_1",
                    "1_0_android.preference.PreferenceManager.getDefaultSharedPreferences_1",
                    "0_1_android.content.SharedPreferences$Editor.apply_0",
                    "1_1_android.app.AlertDialog$Builder.setTitle_1",
                    "1_1_android.app.AlertDialog$Builder.setPositiveButton_2",
                    "1_1_android.content.SharedPreferences$Editor.putInt_2",
                    "1_1_android.app.AlertDialog$Builder.setMessage_1 -> 1_1_android.app.AlertDialog$Builder.setPositiveButton_2",
                    "1_0_android.preference.PreferenceManager.getDefaultSharedPreferences_1 -> 1_1_android.content.SharedPreferences.edit_0",
                    "0_1_android.app.AlertDialog$Builder.show_0 -> 1_0_android.preference.PreferenceManager.getDefaultSharedPreferences_1",
                    "1_1_android.content.SharedPreferences$Editor.putInt_2 -> 0_1_android.content.SharedPreferences$Editor.apply_0",
                    "1_1_android.app.AlertDialog$Builder.setTitle_1 -> 1_1_android.app.AlertDialog$Builder.setMessage_1",
                    "1_1_android.app.AlertDialog$Builder.setPositiveButton_2 -> 0_1_android.app.AlertDialog$Builder.show_0",
                    "1_1_android.content.SharedPreferences.edit_0 -> 1_1_android.content.SharedPreferences$Editor.putInt_2",
                    "0_1_android.app.AlertDialog$Builder.<init>_1 -> 1_1_android.app.AlertDialog$Builder.setTitle_1"]

        for feat in featExtractor.get_features():
            self.assertTrue(feat.desc in features)

    """
    def test_db_insertion(self):
        test_path = os.path.abspath(os.path.dirname(fixrgraph.test.__file__))
        graph_path = os.path.join(test_path, TestSig.ALL_GRAPH_PATH)

        self.clean_db()

        process_graphs(graph_path,
                       TestSig.ADDRESS,
                       TestSig.USER,
                       TestSig.PASSWORD,
                       TestSig.DBNAME)


        # Test number of insert features
        featDb = FeatDb(TestSig.ADDRESS,
                        TestSig.USER,
                        TestSig.PASSWORD,
                        TestSig.DBNAME)
        featDb.open()


        num_graphs = featDb.count_all_graphs()
        self.assertTrue(len(num_graphs) > 0 and num_graphs[0] == 6)

        # Test queries on features
        to_consider = [Feat(Feat.METHOD_CALL, '0_1_android.app.AlertDialog$Builder.show_0'),
                       Feat(Feat.METHOD_EDGE, '0_0_EQ_2')]
        count_res = featDb.count_features(to_consider)
        self.assertTrue(count_res == 1)



        single_graph_path = os.path.join(test_path, TestSig.GRAPH_PATH)
        p_value = compute_p_value(single_graph_path,
                                  featDb)


        featDb.close()

        self.assertTrue(p_value >= 0.0 and p_value <= 0.01)
        """

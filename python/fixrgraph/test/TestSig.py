""" Test the glue code

 """

import fixrgraph
from fixrgraph.stat_sig.feat import (FeatExtractor, Feat)

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

    GRAPH_PATH = "test_data/groums/tv.acfun.a63.MainActivity_showLastPublicReleaseAlert.acdfg.bin"

    def test_feature_extraction(self):
        test_path = os.path.abspath(os.path.dirname(fixrgraph.test.__file__))
        file_path = os.path.join(test_path, TestSig.GRAPH_PATH)

        featExtractor = FeatExtractor(file_path)

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

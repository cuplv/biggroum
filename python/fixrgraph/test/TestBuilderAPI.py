""" Test the access to the builder APIs """

from fixrgraph.extraction.processor import AppBuilderAPI
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


class TestBuilderAPI(unittest.TestCase):

    def test_api(self):
        test_path = os.path.abspath(os.path.dirname(fixrgraph.test.__file__))
        test_data_path = os.path.join(test_path, "test_data")
        buildable_list = os.path.join(test_data_path, "buildable_small.json")
        build_data = os.path.join(test_data_path, "build-data")

        app_builder = AppBuilderAPI(buildable_list, build_data)

        self.assertIsNotNone(app_builder.lookup_build_info("learning-android",
                                                           "Yamba",
                                                           "46795d3c4a1f56416f88a18b708d9db36a429025"))

        self.assertIsNone(app_builder.lookup_build_info("learning-android",
                                                        "wrongrepo",
                                                        "46795d3c4a1f56416f88a18b708d9db36a429025"))


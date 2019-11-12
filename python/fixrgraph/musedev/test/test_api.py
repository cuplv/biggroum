""" Test the creation of the index

"""

import sys
import logging
import os
import json

from cStringIO import StringIO

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from fixrgraph.musedev.biggroumscript import main
from fixrgraph.musedev.api import biggroum_api_map

class TestScript(unittest.TestCase):
    FILEPATH = os.path.join(os.path.dirname(__file__), "test_data")
    JAVAFILE = "AwesomeApp/app/src/main/java/fixr/plv/colorado/edu/awesomeapp/MainActivity.java"
    COMMIT = "04f68b69a6f9fa254661b481a757fa1c834b52e1"

    def test_validate(self):
        myinput = StringIO()
        outstream = StringIO()
        self.assertTrue(main(["biggroumscript.py",
                              TestScript.FILEPATH,
                              TestScript.COMMIT,
                              "applicable"],
                             myinput,
                             outstream,
                             biggroum_api_map) == 0)
        self.assertTrue(outstream.getvalue() == "true")

    def test_version(self):
        myinput = StringIO()
        outstream = StringIO()

        self.assertTrue(main(["biggroumscript.py",
                              TestScript.FILEPATH,
                              TestScript.COMMIT,
                              "version"],
                             myinput,
                             outstream,
                             biggroum_api_map) == 0)
        self.assertTrue(outstream.getvalue() == "3")


    def test_run(self):
        # Mock for calling run multiple times
        runs = []
        for file_name in [TestScript.JAVAFILE, TestScript.JAVAFILE]:
            runs.append({"cwd" : "", "cmd" : "", "args" : "",
                         "classpath" : [],
                         "files": [file_name]})

        residue = {"residue" : {}}
        for run in runs:
            outstream = StringIO()

            myinput = StringIO()
            run["residue"] = residue["residue"]
            myinput.write(json.dumps(run))
            myinput.reset()

            self.assertTrue(main(["biggroumscript.py", TestScript.FILEPATH,
                                  TestScript.COMMIT, "run"],
                                 myinput, outstream, biggroum_api_map) == 0)

            try:
                residue_json = outstream.getvalue()
                residue = json.loads(residue_json)
            except:
                raise Exception("Malformed JSON")

        expected_res = {
            "residue": {
                "compilation_infos" : [{"cwd" : "", "cmd" : "", "args" : "",
                                        "classpath" : [],
                                        "files": [file_name]},
                                       {"cwd" : "", "cmd" : "", "args" : "",
                                        "classpath" : [],
                                        "files": [file_name]}
                ]},
            "toolNotes": []
        }

        # print json.dumps(residue, sort_keys=True)
        # print json.dumps(expected_res, sort_keys=True)

        self.assertTrue(json.dumps(residue, sort_keys=True) ==
                        json.dumps(expected_res, sort_keys=True))

    # def test_finalize(self):
    #     myinput, outstream = StringIO(), StringIO()
    #     myinput.write(json.dumps({}))

    #     self.assertTrue(main(["biggroumscript.py", "aaa","aaa", "finalize"], myinput, outstream, biggroum_api_map) == 0)

    def test_talk(self):
        myinput, outstream = StringIO(), StringIO()
        myinput.write(json.dumps({}))

        self.assertTrue(main(["biggroumscript.py", "aaa","aaa", "talk"], myinput, outstream,
                             biggroum_api_map) == 0)

    def test_reaction(self):
        myinput, outstream = StringIO(), StringIO()
        myinput.write(json.dumps({}))

        self.assertTrue(main(["biggroumscript.py", "aaa","aaa", "reaction"], myinput, outstream,
                             biggroum_api_map) == 0)

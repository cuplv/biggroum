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

from biggroumscript import main

# Hold on on this
# @contextmanager
# from contextlib import contextmanager
# def captured_output():
#     new_out, new_err = StringIO(), StringIO()
#     old_out, old_err = sys.stdout, sys.stderr
#     try:
#         sys.stdout, sys.stderr = new_out, new_err
#         yield sys.stdout, sys.stderr
#     finally:
#         sys.stdout, sys.stderr = old_out, old_err


class TestScript(unittest.TestCase):
    FILEPATH = os.path.join(os.path.dirname(__file__),
                            "test_data/AwesomeApp/app/src/main/java/fixr/plv/colorado/edu/awesomeapp/MainActivity.java")

    COMMIT = "04f68b69a6f9fa254661b481a757fa1c834b52e1"

    def test_validate(self):
        myinput = StringIO()
        outstream = StringIO()

        self.assertTrue(main(["biggroumscript.py", "aaa","aaa", "applicable"], myinput, outstream) == 0)
        self.assertTrue(outstream.getvalue() == "true")

    def test_version(self):
        myinput = StringIO()
        outstream = StringIO()

        self.assertTrue(main(["biggroumscript.py", "aaa","aaa", "version"], myinput, outstream) == 0)
        self.assertTrue(outstream.getvalue() == "3")


    def test_run(self):
        # Mock for calling run multiple times
        runs = []
        for file_name in ["./test_data/app/src/main/java/fixr/plv/colorado/edu/awesomeapp/MainActivity.java",
                          "./test_data/app/src/main/java/fixr/plv/colorado/edu/awesomeapp/MainActivity.java"]:
            runs.append({
                "cwd" : "",
                "cmd" : "",
                "args" : "",
                "classpath" : [],
                    "files": [],
                "residue": {}
            })

        # TODO: Add the results for residues
        results = [
            {"residue": {}, "toolNotes": []},
            {"residue": {}, "toolNotes": []}
        ]
        for run,expected_res in zip(runs, results):
            myinput = StringIO()
            outstream = StringIO()

            myinput.write(json.dumps(run))

            self.assertTrue(main(["biggroumscript.py", run, TestScript.COMMIT, "run"],
                                 myinput, outstream) == 0)

            try:
                res = json.loads(outstream.getvalue())
            except:
                raise Exception("Malformed JSON")

            self.assertTrue(json.dumps(res, sort_keys=True) ==
                            json.dumps(expected_res, sort_keys=True))

    def test_finalize(self):
        myinput, outstream = StringIO(), StringIO()
        myinput.write(json.dumps({}))

        self.assertTrue(main(["biggroumscript.py", "aaa","aaa", "finalize"], myinput, outstream) == 0)

    def test_finalize(self):
        myinput, outstream = StringIO(), StringIO()
        myinput.write(json.dumps({}))

        self.assertTrue(main(["biggroumscript.py", "aaa","aaa", "finalize"], myinput, outstream) == 0)

    def test_talk(self):
        myinput, outstream = StringIO(), StringIO()
        myinput.write(json.dumps({}))

        self.assertTrue(main(["biggroumscript.py", "aaa","aaa", "talk"], myinput, outstream) == 0)

    def test_reaction(self):
        myinput, outstream = StringIO(), StringIO()
        myinput.write(json.dumps({}))

        self.assertTrue(main(["biggroumscript.py", "aaa","aaa", "reaction"], myinput, outstream) == 0)

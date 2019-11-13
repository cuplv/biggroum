""" Test the creation of the index

"""

import sys
import logging
import os
import json
import copy
import subprocess

from fixrgraph.pipeline.pipeline import Pipeline


from cStringIO import StringIO

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from fixrgraph.musedev.biggroumscript import main
from fixrgraph.musedev.api import biggroum_api_map
from fixrgraph.musedev.residue import Residue


def compare_json_obj(obj1, obj2):
    return json.dumps(obj1, sort_keys=True) == json.dumps(obj2, sort_keys=True)

def get_logger():
    logging.basicConfig(stream=sys.stderr, level=logging.ALL)
    logger = logging.getLogger('biggroumscript')
    return logger

class TestScript(unittest.TestCase):
    FILEPATH = os.path.join(os.path.dirname(__file__), "data")
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

        self.assertTrue(compare_json_obj(residue, expected_res))

    def test_finalize(self):
        os.environ["GRAPHEXTRACTOR"] = os.sep.join([os.path.dirname(__file__),
                                                    "..","..","..","..","FixrGraphExtractor",
                                                    "target","scala-2.12","fixrgraphextractor_2.12-0.1.0-one-jar.jar"])
        myinput, outstream = StringIO(), StringIO()
        main_act_path = os.path.join(os.path.dirname(__file__),
                                     "data/AwesomeApp/app/src/main/java/fixr/plv"
                                     "/colorado/edu/awesomeapp/MainActivity.java")
        input_res = {
            "residue": {
                "compilation_infos" : [{"cwd" : "", "cmd" : "", "args" : "",
                                        "classpath" : [],
                                        "files": [main_act_path]}
                                       ]},
            "toolNotes": []
        }
        myinput.write(json.dumps(input_res))
        myinput.reset()
        # TODO: add test when implementation is done

        self.assertTrue(main(["biggroumscript.py", TestScript.FILEPATH,
                              TestScript.COMMIT, "finalize"],
                             myinput, outstream, biggroum_api_map) == 0,get_logger())
        # self.assertTrue(main(["biggroumscript.py", "aaa","aaa", "finalize"], myinput, outstream, biggroum_api_map) == 0)

    def test_talk(self):
        residue_empty = {
            "anomalies" : {}
        }

        inputs_errors = [
            {"residue" : {}, "messageText" : "biggroum", "user" : "", "noteID" : ""},
            {"residue" : {}, "messageText" : "biggroum wrongrequest", "user" : "", "noteID" : ""},
            {"residue" : {}, "messageText" : "biggroum inspect", "user" : ""},
            {"residue" : {}, "messageText" : "biggroum pattern", "user" : ""},
            {"residue" : residue_empty, "messageText" : "biggroum inspect", "user" : "", "noteID" : "1"},
            {"residue" : residue_empty, "messageText" : "biggroum pattern", "user" : "", "noteID" : "1"},
        ]


        for single_input in inputs_errors:
            myinput, outstream = StringIO(), StringIO()
            myinput.write(json.dumps(single_input))
            myinput.reset()
            self.assertTrue(main(["biggroumscript.py", TestScript.FILEPATH, TestScript.COMMIT, "talk"],
                                 myinput, outstream, biggroum_api_map) != 0)

        residue = {
            "anomalies" : {
                "1" : {},
                "2" : {}
            }
        }

        myinput, outstream = StringIO(), StringIO()
        myinput.write(json.dumps({"residue" : residue,
                                  "messageText" : "biggroum inspect",
                                  "user" : "", "noteID" : u'1'},))
        myinput.reset()
        self.assertTrue(main(["biggroumscript.py", TestScript.FILEPATH, TestScript.COMMIT, "talk"],
                             myinput, outstream, biggroum_api_map) == 0)

        myinput, outstream = StringIO(), StringIO()
        myinput.write(json.dumps({"residue" : residue,
                                  "messageText" : "biggroum pattern",
                                  "user" : "", "noteID" : "1"},))
        myinput.reset()
        self.assertTrue(main(["biggroumscript.py", TestScript.FILEPATH, TestScript.COMMIT, "talk"],
                             myinput, outstream, biggroum_api_map) == 0)




    def test_reaction(self):
        myinput, outstream = StringIO(), StringIO()
        myinput.write(json.dumps({}))
        myinput.reset()

        self.assertTrue(main(["biggroumscript.py", "aaa","aaa", "reaction"], myinput, outstream,
                             biggroum_api_map) == 0)


class TestResiude(unittest.TestCase):
    def test_compilation_info(self):
        def test_res(residue, expected_residue, ci, fi):
            self.assertTrue(compare_json_obj(residue, expected_residue))
            self.assertTrue(compare_json_obj(Residue.get_compilation_infos(residue), ci))

            res_files = []
            for ci in Residue.get_compilation_infos(residue):
                res_files = res_files + Residue.get_files(ci)
            self.assertTrue(set(fi) == set(res_files))

        f1 = ["file1", "file2"]
        f2 = ["file3", "file4"]
        ci1 = {
            "cwd" : "cwd",
            "cmd" : "cmd",
            "args" : "args",
            "classpath" : "classpath",
            "files" : f1,
        }
        ci2 = copy.deepcopy(ci1)
        ci2["files"] = f2

        expected_residue = {"compilation_infos" : [ci1]}
        residue = Residue.append_compilation_info(None, ci1)
        test_res(residue, expected_residue, [ci1], f1)

        expected_residue = {"compilation_infos" : [ci1,ci2]}
        residue = Residue.append_compilation_info(residue, ci2)
        test_res(residue, expected_residue, [ci1,ci2], f1+f2)


    def test_anomaly(self):
        # TODO: replace with a real anomaly
        anomaly1 = {}
        anomaly2 = {}
        anomaly3 = {}

        residue = Residue.store_anomaly(None, anomaly1, "1")
        self.assertTrue(compare_json_obj(residue, {"anomalies" : {"1" : anomaly1}}))

        residue = Residue.store_anomaly(residue, anomaly2, "2")
        residue = Residue.store_anomaly(residue, anomaly3, "3")

        self.assertTrue(compare_json_obj(anomaly1,
                                         Residue.retrieve_anomaly(residue, "1")))
        self.assertTrue(compare_json_obj(anomaly2,
                                         Residue.retrieve_anomaly(residue, "2")))
        self.assertTrue(compare_json_obj(anomaly3,
                                         Residue.retrieve_anomaly(residue, "3")))


class TestBash(unittest.TestCase):
    SCRIPTPATH = "biggroumcheck.sh"

    def test_bash(self):
        previous = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        exec_file = os.path.join(previous, TestBash.SCRIPTPATH)

        # Must fail, wrong command
        args = [exec_file, TestScript.FILEPATH, TestScript.COMMIT, "nothing"]
        self.assertFalse(Pipeline._call_sub(args, previous))

        # Must succeed on the run command
        script_input = {
            "residue" : {},
            "cwd" : "",
            "cmd" : "",
            "args" : "",
            "classpath" : [],
            "files" : ["file1.java", "file2.java"]
        }
        args = [exec_file, TestScript.FILEPATH, TestScript.COMMIT, "run"]
        proc = subprocess.Popen(args, cwd=previous,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        # Write the output
        proc.stdin.write(json.dumps(script_input))
        stdout, stderr = proc.communicate()
        proc.wait()
        proc.stdin.close()

        return_code = proc.returncode

        self.assertTrue(return_code == 0)

        compare_json_obj(json.loads(stdout),
                         {
                             "toolNotes" : [],
                             "residue" : {
                                 "compilation_infos" : script_input
                             }
                         }
        )

""" Test the creation of the index

"""

import sys
import logging
import os
import StringIO
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
        myinput = StringIO()
        outstream = StringIO()

        myinput.write(json.dumps({}))

        self.assertTrue(main(["biggroumscript.py", "aaa","aaa", "run"], myinput, outstream) == 0)
        # self.assertTrue(outstream.getvalue() == "")

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

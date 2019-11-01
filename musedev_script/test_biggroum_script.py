""" Test the creation of the index

"""

import sys
import logging
import os
import StringIO

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
        main(["biggroumscript.py", "aaa","aaa", "applicable"], myinput, outstream)

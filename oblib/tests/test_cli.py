# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 15:06:01 2019

@author: cliff
"""

import unittest
import os
import subprocess
from oblib import identifier, ob, taxonomy, validator

PIPE = subprocess.PIPE
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
OBLIB_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
CLI = os.path.join(OBLIB_DIR, 'cli.py')

class TestCLI(unittest.TestCase):

    def test_help(self):
        result = subprocess.run(["python", CLI, "-h"],
                                stdout=PIPE, stderr=PIPE)
        text = result.stdout.decode('utf-8')
        self.assertTrue('usage: cli.py' in text)
        self.assertEqual(result.returncode, 0)
        result = subprocess.run(["python", CLI, "-help"],
                                stdout=PIPE, stderr=PIPE)
        text = result.stdout.decode('utf-8')
        self.assertTrue('usage: cli.py' in text)
        self.assertEqual(result.returncode, 0)

    def test_info(self):
        result = subprocess.run(["python", CLI, "info"],
                                stdout=PIPE, stderr=PIPE)
        self.assertEqual(result.returncode, 1)

    def test_version(self):
        result = subprocess.run(["python", CLI, " version"],
                                stdout=PIPE, stderr=PIPE)
        self.assertEqual(result.returncode, 1)

    def test_validate_identifier(self):
        result = subprocess.run(["python", CLI, "validate-identifier",
                                 "55db4ff3-5136-4be5-846b-4a93eb4c576d"],
                                stdout=PIPE, stderr=PIPE)
        text = result.stdout.decode('utf-8')
        print(result)
        self.assertIn('Valid: True', text)
        self.assertEqual(result.returncode, 1)
        result = subprocess.run(["python", CLI, " validate-identifier",
                                 "55db4ff3-5136-4be5-846b-4a93eb4c576"],
                                stdout=PIPE, stderr=PIPE)
        text = result.stdout.decode('utf-8')
        self.assertIn('Valid: False', text)
        self.assertEqual(result.returncode, 1)
        result = subprocess.run(["python", CLI, " validate-identifier"],
                                stdout=PIPE, stderr=PIPE)
        self.assertEqual(result.returncode, 2)


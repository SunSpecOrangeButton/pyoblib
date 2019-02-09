# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 15:06:01 2019

@author: cliff
"""

import os
import subprocess

PIPE = subprocess.PIPE
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
OBLIB_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
CLI = os.path.join(OBLIB_DIR, 'cli.py')

result = subprocess.run(["python " + CLI + " -h"], stdout=PIPE, stderr=PIPE)


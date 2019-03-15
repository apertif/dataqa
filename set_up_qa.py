#!/usr/bin/env python

"""
This script creates the directory structure for the
quality assessment of the science demonstration period 2019.

It will create the directoris in /home/<user>/science_demo_2019/

(It can also be written in a way that it copies the python files
from the cloned repo to the new directory if the OAS should work in there)

Parameter
    obs_id : int
        Observation number which should be assessed

Example:
    python set_up_qa.py obs_id

"""

import argparse
import os
import numpy as np
import glob
import socket
import sys

# Create and parse argument list
# ++++++++++++++++++++++++++++++
parser = argparse.ArgumentParser(
    description='Create directory structure for QA of an observation')

# 1st argument: Observation number
parser.add_argument("obs_id", type=int,
                    help='Observation Number')

args = parser.parse_args()

# Basic parameters
# ++++++++++++++++

obs_id = args.obs_id

qa_dir_list = ['crosscal', 'selfcal', 'continuum', 'line', 'mosaic']

print("Creating directories for QA of observation {0:d}".format(obs_id))

# Check what host the user is on
# ++++++++++++++++++++++++++++++

host_name = socket.gethostname()

if host_name != "happili-01":
    print("WARNING: You are not working on happili-01")
    print("WARNING: Not all QA script may work or will work only on a subset of beams")
    print("WARNING: Please switch to happili-01")

# Check that the observation exists
# ++++++++++++++++++++++++++++++++++

# base directory for data
if host_name != "happili-01":
    data_basedir_list = ['/data/apertif/']
else:
    data_basedir_list = ['/data/apertif/', '/data2/apertif/',
                         '/data3/apertif/', '/data4/apertif/']

# number of data directories
n_data_dir = len(data_basedir_list)

# create data directories
data_dir_list = ["{0:s}{1:d}".format(basedir, obs_id)
                 for basedir in data_basedir_list]

# go through the data directories and check that they exist
missing_dir = 0
for data_dir in data_dir_list:

    if os.path.exists(data_dir):

        # get the beams in the directory
        beam_list = glob.glob('{0:s}/[0-3][0-9]')

        # show what beams were found
        print("Found {0:d} beams in {1:s}".format(obs_id, data_dir))

    else:
        missing_dir += 1
        print("Warning: No beams found for observation {0:d} in {1:s}".format(
            obs_id, data_dir))

# Create directories for QA
# +++++++++++++++++++++++++

# if no data for an observation exists, abort process
if missing_dir == n_data_dir:
    print("ERROR: Did not found any data for observation {0:d}".format(obs_id))
    sys.exit(-1)

# get home directory
home_dir = os.path.expanduser('~')

# get main directory
main_dir = "{0:s}/qa_science_demo_2019".format(home_dir)

# check/create main directory
if os.path.exists(main_dir):
    print("Directory {0:s} already exists. Continue".format(main_dir))
else:
    print("Created directory {0:s}".format(main_dir))
    os.mkdir(main_dir)

# check/create observation directory
obs_dir = "{0:s}/{1:d}".format(main_dir, obs_id)
if os.path.exists(obs_dir):
    print("Directory {0:s} already exists. Continue".format(obs_dir))
else:
    print("Created directory {0:s}".format(obs_dir))
    os.mkdir(obs_dir)

# check/create the subdirectories
for sub_dir in qa_dir_list:

    # full directory path
    qa_dir = "{0:s}/{1:s}".format(obs_dir, sub_dir)

    if os.path.exists(qa_dir):
        print("Directory {0:s} already exists. Continue".format(qa_dir))
    else:
        print("Created directory {0:s}".format(qa_dir))
        os.mkdir(qa_dir)

print("Creating QA directories done.")

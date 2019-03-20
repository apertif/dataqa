#!/usr/bin/env python

"""
This script contains functionality to run pybdsf on continuum data
for the QA

It does can run on a single image for the mosaic QA or an observation
number alone for the continuum QA. In the latter case, it will go through
all the beams.

There will be a log file either in
/home/<user>/qa_science_demo_2019/<obs_id>/continuum/<beam>/pybdsf
or
/home/<user>/qa_science_demo_2019/<obs_id>/mosaic/pybdsf
"""

import argparse
import numpy as np
import logging
import bdsf
import os
import time
import logging
import socket
from apercal.libs import lib
import sys
import glob
from dataqa.scandata import get_default_imagepath
from dataqa.continuum.qa_continuum import qa_continuum_run_pybdsf_validation
from dataqa.continuum.qa_continuum import qa_get_image_noise_dr_gaussianity
from dataqa.mosaic.qa_mosaic import qa_mosaic_run_pybdsf_validation


if __name__ == '__main__':

    start_time = time.time()

    # Create and parse argument list
    # ++++++++++++++++++++++++++++++
    parser = argparse.ArgumentParser(
        description='Create directory structure for qa of an observation')

    # main argument: Observation number
    parser.add_argument("obs_id", type=int,
                        help='Observation Number')

    # Optional argument
    parser.add_argument("--overwrite", action="store_true", default=True,
                        help='Overwrite existing files')

    parser.add_argument("--beam", type=list, default=[],
                        help='Specify a single beam or a list of beams to run pybdsf')

    parser.add_argument("-p", "--path", type=str, default=None,
                        help='Directory to store the output in')

    parser.add_argument("--mosaic_name", type=str, default='',
                        help='Provide name of the moasic image. This will run pybdsf only on this image')

    # parser.add_argument("--n_processes", type=int, default=1,
    #                     help='Number of cores to use for processing')

    args = parser.parse_args()

    # Check what host the user is on
    # ++++++++++++++++++++++++++++++

    host_name = socket.gethostname()

    if host_name != "happili-01":
        print("WARNING: You are not working on happili-01.")
        print("WARNING: The script will not process all beams")
        print("Please switch to happili-01")

    # Basic parameters
    # ++++++++++++++++

    # get the observation number
    obs_id = args.obs_id

    # users home directory
    # home_dir = os.path.expanduser('~')

    # the mode in which the script runs
    # beam: run on a single beam
    # mosaic: run on a file
    run_mode = 'continuum'

    if args.mosaic_name != '':
        mosaic_name = args.mosaic_name
        run_mode = 'mosaic'
    else:
        mosaic_name = ''

    # directory where the output will be of pybdsf will be stored
    if args.path is None:
        qa_dir = get_default_imagepath(args.scan)
    else:
        qa_dir = args.path

    if run_mode == 'continuum':
        qa_pybdsf_dir = "{0:s}/continuum".format(
            qa_dir)
    else:
        qa_pybdsf_dir = "{0:s}/mosaic".format(
            qa_dir)

    # check that this directory exists (just in case)
    if not os.path.exists(qa_pybdsf_dir):
        print("Directory {0:s} does not exist and will be created".format(
            qa_pybdsf_dir))
        os.mkdir(qa_pybdsf_dir)

    # 'create another directory to store the pybdsf output
    qa_pybdsf_dir = '{0:s}/pybdsf'.format(qa_pybdsf_dir)
    if not os.path.exists(qa_pybdsf_dir):
        print("Directory {0:s} does not exist and will be created".format(
            qa_pybdsf_dir))
        os.mkdir(qa_pybdsf_dir)

    # base directory for data
    if host_name != "happili-01":
        data_basedir_list = ['/data/apertif/']
    else:
        data_basedir_list = ['/data/apertif/', '/data2/apertif/',
                             '/data3/apertif/', '/data4/apertif/']

    # Run PyBDSF depending on the chosen mode
    # +++++++++++++++++++++++++++++++++++++++

    # Create logging file
    lib.setup_logger(
        'debug', logfile='{0:s}/{1:d}_{2:s}_pybdsf.log'.format(qa_pybdsf_dir, obs_id, run_mode))
    logger = logging.getLogger(__name__)

    # logging.basicConfig(filename='{0:s}/{1:d}_{2:s}_pybdsf.log'.format(qa_pybdsf_dir, obs_id, run_mode), level=logging.DEBUG,
    #                     format='%(asctime)s - %(levelname)s: %(message)s')

    # logger = logging.getLogger(__name__)

    # run through continuum mode
    if run_mode == 'continuum':
        pybdsf_run_status = qa_continuum_run_pybdsf_validation(
            data_basedir_list, qa_pybdsf_dir)
        if pybdsf_run_status == 1:
            logger.info("Finished pybdsf and validation tool successfully.")
        else:
            logger.error(
                "Did not finish pybdsf and validation tool successfully. Check logfile")
    # run through mosaic mode
    else:
        # check that the file name exists
        if os.path.exists(mosaic_name):
            logger.info("Found image file {0:s}".format(mosaic_name))
        else:
            logger.error(
                "Image {0:s} not found. Abort".format(mosaic_name))

        # run the validation tool and pybdsf
        pybdsf_run_status = qa_mosaic_run_pybdsf_validation(
            mosaic_name, qa_pybdsf_dir)
        if pybdsf_run_status == 1:
            logger.info("Finished pybdsf and validation tool successfully")
        else:
            logger.error(
                "Did not finish pybdsf and validation tool successfully. Check logfile")

        # Get additional QA information
        qa_get_image_noise_dr_gaussianity(mosaic_name, qa_pybdsf_dir)

    logger.info("Running pybdsf for {0:d} done. (time {1:.0f}s)".format(
        obs_id, time.time()-start_time))

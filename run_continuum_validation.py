#!/usr/bin/env python

"""
This script contains functionality to run pybdsf on continuum data
for the QA

It does can run on a single image for the mosaic QA or an observation
number alone for the continuum QA. In the latter case, it will go through
all the beams.
"""

import argparse
import numpy as np
import logging

# Need to do this before bdsf import, it sets the default matplotlib backend
import matplotlib
matplotlib.use('Agg')

import bdsf
import os
import time
import logging
import socket
from apercal.libs import lib
import sys
import glob
from dataqa.scandata import get_default_imagepath
from dataqa.continuum.qa_continuum import qa_continuum_run_validation
from dataqa.continuum.qa_continuum import qa_get_image_noise_dr_gaussianity
from dataqa.mosaic.qa_mosaic import qa_mosaic_run_validation


if __name__ == '__main__':

    start_time = time.time()

    # Create and parse argument list
    # ++++++++++++++++++++++++++++++
    parser = argparse.ArgumentParser(
        description='Run validation for continuum or mosaic QA')

    # main argument: Observation number
    parser.add_argument("obs_id", type=str,
                        help='Observation Number / Scan Number / TASK-ID')

    # Optional argument
    parser.add_argument("--mosaic_name", type=str, default='',
                        help='Provide name of the moasic image. This will run the validation only on this image.')

    # Optional argument
    parser.add_argument("--for_mosaic", action="store_true", default=False,
                        help='Set to run for mosaic QA.')

    # this mode will make the script look only for the beams processed by Apercal on a given node
    parser.add_argument("--trigger_mode", action="store_true", default=False,
                        help='Set it to run Autocal triggering mode automatically after Apercal.')

    # parser.add_argument("--overwrite", action="store_true", default=True,
    #                     help='Overwrite existing files')

    # parser.add_argument("--beam", type=list, default=[],
    #                     help='Specify a single beam or a list of beams to run pybdsf')

    parser.add_argument("-p", "--path", type=str, default=None,
                        help='Directory to store the output in')

    parser.add_argument("-b", "--basedir", type=str, default=None,
                        help='Data directory without taskid')

    # parser.add_argument("--n_processes", type=int, default=1,
    #                     help='Number of cores to use for processing')

    args = parser.parse_args()

    # Check what host the user is on
    # ++++++++++++++++++++++++++++++

    host_name = socket.gethostname()

    if host_name != "happili-01" and not args.trigger_mode:
        print("INFO: You are not working on happili-01.")
        print("INFO: The script will not process all beams")
        print("Please switch to happili-01")

    # Basic parameters
    # ++++++++++++++++

    # get the observation number
    obs_id = args.obs_id

    # users home directory
    # home_dir = os.path.expanduser('~')

    # the mode in which the script runs
    # mosaic: run on a file
    if args.for_mosaic or args.mosaic_name != '':
        run_mode = 'mosaic'
    else:
        run_mode = 'continuum'

    # directory where the output will be of pybdsf will be stored
    if args.path is None:
        qa_dir = get_default_imagepath(obs_id, basedir=args.basedir)

        # check that path exists
        if not os.path.exists(qa_dir):
            print(
                "Directory {0:s} does not exist and will be created".format(qa_dir))
            os.mkdir(qa_dir)
    else:
        qa_dir = args.path

    # check the mode to run the validation
    if run_mode == 'continuum':
        qa_validation_dir = "{0:s}continuum".format(
            qa_dir)
    else:
        qa_validation_dir = "{0:s}mosaic".format(
            qa_dir)

    # check that this directory exists (just in case)
    if not os.path.exists(qa_validation_dir):
        print("Directory {0:s} does not exist and will be created".format(
            qa_validation_dir))
        os.mkdir(qa_validation_dir)

    # # 'create another directory to store the pybdsf output
    # qa_validation_dir = '{0:s}/validation'.format(qa_validation_dir)
    # if not os.path.exists(qa_validation_dir):
    #     print("Directory {0:s} does not exist and will be created".format(
    #         qa_validation_dir))
    #     os.mkdir(qa_validation_dir)

    # Run validation depending on the chosen mode
    # +++++++++++++++++++++++++++++++++++++++++++

    # Create logging file
    lib.setup_logger(
        'debug', logfile='{0:s}/{1:s}_{2:s}_validation.log'.format(qa_validation_dir, obs_id, run_mode))
    logger = logging.getLogger(__name__)

    # logging.basicConfig(filename='{0:s}/{1:d}_{2:s}_pybdsf.log'.format(qa_validation_dir, obs_id, run_mode), level=logging.DEBUG,
    #                     format='%(asctime)s - %(levelname)s: %(message)s')

    # logger = logging.getLogger(__name__)

    # run through continuum mode
    if run_mode == 'continuum':

        # base directory for data
        if args.trigger_mode:
            logger.info(
                "--> Running continuum QA in trigger mode. Looking only for data processed by Apercal on {0:s} <--".format(host_name))
            data_basedir_list = ['/data/apertif/{0:s}'.format(obs_id)]
        elif host_name != "happili-01":
            data_basedir_list = ['/data/apertif/{0:s}'.format(obs_id)]

        else:
            data_basedir_list = ['/data/apertif/{0:s}'.format(obs_id), '/data2/apertif/{0:s}'.format(obs_id),
                                 '/data3/apertif/{0:s}'.format(obs_id), '/data4/apertif/{0:s}'.format(obs_id)]

        # run the continuum validation (with pybdsf)
        try:
            qa_continuum_run_validation(data_basedir_list, qa_validation_dir)
        except Exception as e:
            logger.error(e)
            logger.error("Running continuum validation was not successful")

        # # that it ran through
        # if validation_run_status == 1:
        #     logger.info("Finished pybdsf and validation tool successfully.")
        # else:
        #     logger.error(
        #         "Did not finish pybdsf and validation tool successfully. Check logfile")

    # run through mosaic mode
    else:
        if args.mosaic_name == '':
            mosaic_name = "/data/apertif/{0:s}/mosaic/{0:s}_mosaic_image.fits".format(
                obs_id)
        else:
            mosaic_name = args.mosaic_name
        # check that the file name exists
        if os.path.exists(mosaic_name):
            logger.info("Found image file {0:s}".format(mosaic_name))
        else:
            logger.error(
                "Image {0:s} not found. Abort".format(mosaic_name))

        # run the validation tool with pybdsf
        try:
            qa_mosaic_run_validation(mosaic_name, qa_validation_dir)
        except Exception as e:
            logger.error(e)
            logger.error("Running continuum validation was not successful")

        # if validation_run_status == 1:
        #     logger.info("Finished pybdsf and validation tool successfully")
        # else:
        #     logger.error(
        #         "Did not finish pybdsf and validation tool successfully. Check logfile")

        # Get additional QA information
        #qa_get_image_noise_dr_gaussianity(mosaic_name, qa_validation_dir)

    logger.info("Running validation for {0:s} done. (time {1:.0f}s)".format(
        obs_id, time.time()-start_time))

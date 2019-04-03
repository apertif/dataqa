import numpy as np
import sys
import os
import argparse
import glob
import socket
import time
import logging
from apercal.libs import lib
from dataqa.scandata import get_default_imagepath
from dataqa.line.cube_stats import get_cube_stats


import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


if __name__ == '__main__':

    start_time = time.time()

    # Create and parse argument list
    # ++++++++++++++++++++++++++++++
    parser = argparse.ArgumentParser(description='Run validation for line QA')

    # main argument: Observation number
    parser.add_argument("obs_id", type=str,
                        help='Observation Number / Scan Number / TASK-ID')

    args = parser.parse_args()

    # get taskid/obs_id/scan
    obs_id = args.obs_id

    # get the QA directory for this observation
    qa_dir = get_default_imagepath(obs_id)

    # get the line QA directory for this observation
    qa_line_dir = "{0:s}line".format(qa_dir)

    if not os.path.exists(qa_line_dir):
        print("Creating directory {0:s}".format(qa_line_dir))
        os.mkdir(qa_line_dir)

    # Create logging file
    lib.setup_logger(
        'debug', logfile='{0:s}/get_cube_stats.log'.format(qa_line_dir))
    logger = logging.getLogger(__name__)

    # check host name
    host_name = socket.gethostname()

    # get data directories depending on the host name
    if host_name != "happili-01":
        logger.warning("You are not working on happili-01.")
        logger.warning("The script will not process all beams")
        logger.warning("Please switch to happili-01")
        data_base_dir_list = ['/data/apertif/{0:s}'.format(obs_id)]
    else:
        data_base_dir_list = ['/data/apertif/{0:s}'.format(obs_id), '/data2/apertif/{0:s}'.format(
            obs_id), '/data3/apertif/{0:s}'.format(obs_id), '/data4/apertif/{0:s}'.format(obs_id)]

    # run the function to get the cube statistics
    # +++++++++++++++++++++++++++++++++++++++++++
    try:
        get_cube_stats(qa_line_dir, data_base_dir_list)
    except Exception as e:
        logger.error(e)

    logger.info("Getting cube statistics. Done ({0:.0f}s)".format(
        time.time()-start_time))

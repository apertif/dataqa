#!/usr/bin/python2.7

"""
Script to create an html overview

# NOTE:
 Crosscal plots are now distributed over notes.

 Preflag plots are also distributed over the notes

"""

import os
import sys
from astropy.table import Table
import logging
import glob
import time
import argparse
import socket
from apercal.libs import lib
from report import html_report as hp
from report import html_report_dir as hpd
from report.pipeline_run_time import get_pipeline_run_time
from scandata import get_default_imagepath

if __name__ == "__main__":

    start_time = time.time()

    # Create and parse argument list
    # ++++++++++++++++++++++++++++++
    parser = argparse.ArgumentParser(
        description='Create overview for QA')

    # 1st argument: Observation number
    parser.add_argument("obs_id", type=str,
                        help='Observation Number')

    parser.add_argument("-p", "--path", type=str,
                        help='Path to QA output')

    # this mode will make the script look only for the beams processed by Apercal on a given node
    parser.add_argument("--trigger_mode", action="store_true", default=False,
                        help='Set it to run Autocal triggering mode automatically after Apercal.')

    args = parser.parse_args()

    obs_id = args.obs_id
    qa_dir = args.path

    # directory where the output will be of pybdsf will be stored
    if qa_dir is None:
        qa_dir = get_default_imagepath(obs_id)

        # check that path exists
        if not os.path.exists(qa_dir):
            print(
                "Directory {0:s} does not exist and will be created".format(qa_dir))
            os.makedirs(qa_dir)

    # check the mode to run the validation
    qa_report_dir = "{0:s}report".format(
        qa_dir)

    # check that this directory exists (just in case)
    if not os.path.exists(qa_report_dir):
        print("Directory {0:s} does not exist and will be created".format(
            qa_report_dir))
        os.makedirs(qa_report_dir)

    lib.setup_logger(
        'debug', logfile='{0:s}/create_report.log'.format(qa_report_dir))
    logger = logging.getLogger(__name__)

    # check first on which happili we are:
    host_name = socket.gethostname()

    if args.trigger_mode:
        logger.info(
            "--> Running continuum QA in trigger mode. Looking only for data processed by Apercal on {0:s} <--".format(host_name))
    elif host_name != "happili-01" and not args.trigger_mode:
        logger.warning("You are not working on happili-01.")
        logger.warning("The script will not process all beams")
        logger.warning("Please switch to happili-01")

    apercal_log_file = "/data/apertif/{0:s}/apercal.log".format(
        obs_id)

    # logging.basicConfig(filename='{0:s}/create_report.log'.format(qa_dir), level=logging.DEBUG,
    #                     format='%(asctime)s - %(levelname)s: %(message)s')

    # getting timing measurment for apercal
    try:
        get_pipeline_run_time(obs_id, trigger_mode=args.trigger_mode)
    except Exception as e:
        logger.error(e)

    # the subpages to be created
    subpages = ['preflag', 'crosscal',
                'continuum', 'selfcal', 'line', 'mosaic', 'apercal_log']

    logger.info("#### Create report directory structure")

    # copy the js and css files
    js_file_name = "{0:s}/report_fct.js".format(
        hp.__file__.split("/html_report.py")[0])
    css_file_name = "{0:s}/report_style.css".format(
        hp.__file__.split("/html_report.py")[0])

    # Check that qa_dir and the other directories exists
    if not os.path.exists(qa_dir):
        logger.error(
            "Directory {0:s} does not exists. Abort".format(qa_report_dir))
        sys.exit(-1)
    else:
        # Create directory structure for the report
        try:
            hpd.create_report_dirs(
                obs_id, qa_dir, subpages, css_file=css_file_name, js_file=js_file_name, trigger_mode=args.trigger_mode)
        except Exception as e:
            logger.error(e)

    logger.info("#### Creating report")

    try:
        hp.create_main_html(qa_report_dir, obs_id, subpages,
                            css_file=css_file_name, js_file=js_file_name)
    except Exception as e:
        logger.error(e)

    logger.info("#### Report. Done ({0:.0f}s)".format(
        time.time()-start_time))

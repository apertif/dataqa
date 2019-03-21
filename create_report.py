#!/usr/bin/python2.7

"""
Test script to create an html overview
"""

import os
import sys
from astropy.table import Table
import logging
import glob
import time
import argparse
from apercal.libs import lib
from dataqa.report import html_report as hp
from dataqa.report import html_report_dir as hpd
from datqa.scandata import get_default_imagepath

if __name__ == "__main__":

    start_time = time.time()

    # Create and parse argument list
    # ++++++++++++++++++++++++++++++
    parser = argparse.ArgumentParser(
        description='Create overview for QA')

    # 1st argument: Observation number
    parser.add_argument("obs_id", type=int,
                        help='Observation Number')

    parser.add_argument("-p", "--path", type=str,
                        help='Path to QA output')

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
            os.mkdir(qa_dir)

    # check the mode to run the validation
    qa_report_dir = "{0:s}report".format(
        qa_dir)

    # check that this directory exists (just in case)
    if not os.path.exists(qa_report_dir):
        print("Directory {0:s} does not exist and will be created".format(
            qa_report_dir))
        os.mkdir(qa_report_dir)

    lib.setup_logger(
        'debug', logfile='{0:s}/create_report.log'.format(qa_report_dir))
    logger = logging.getLogger(__name__)

    # logging.basicConfig(filename='{0:s}/create_report.log'.format(qa_dir), level=logging.DEBUG,
    #                     format='%(asctime)s - %(levelname)s: %(message)s')

    # the subpages to be created
    subpages = ['prepare', 'crosscal',
                'continuum', 'selfcal', 'line', 'mosaic', 'apercal_log']

    logger.info("#### Create report directory structure")

    # copy the js and css files
    js_file_name = "report/report_fct.js"
    css_file_name = "report/report_style.css"

    # Check that qa_dir and the other directories exists
    if not os.path.exists(qa_dir):
        logger.error("Directory {0:s} does not exists. Abort".format(qa_dir))
        sys.exit(-1)
    else:
        # Create directory structure for the report
        create_dir_stat = hpd.create_report_dirs(
            obs_id, qa_dir, subpages, css_file=css_file_name, js_file=js_file_name)

    logger.info("### Creating report")

    create_main_html_stat = hp.create_main_html(
        qa_dir, obs_id, subpages, css_file=css_file_name, js_file=js_file_name)

    if create_main_html_stat == 1:
        logger.info("Creating report succesfull")
    else:
        logger.error("Creating report failed")

    logger.info("Report. Done ({0:.0f}s)".format(
        time.time()-start_time))

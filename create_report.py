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
from report import html_report as hp
from report import html_report_dir as hpd

if __name__ == "__main__":

    start_time = time.time()

    # Create and parse argument list
    # ++++++++++++++++++++++++++++++
    parser = argparse.ArgumentParser(
        description='Create overview for QA')

    # 1st argument: Observation number
    parser.add_argument("obs_id", type=int,
                        help='Observation Number')

    parser.add_argument("--qa_dir", type=str, default='',
                        help='Observation Number')

    args = parser.parse_args()

    obs_id = args.obs_id
    qa_dir = args.qa_dir

    logging.basicConfig(filename='{0:s}/create_report.log'.format(qa_dir), level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s: %(message)s')

    # the subpages to be created
    subpages = ['prepare', 'crosscal',
                'continuum', 'selfcal', 'line', 'mosaic', 'apercal_log']

    print("Create report directory structure")

    # copy the js and css files
    js_file_name = "report/report_fct.js"
    css_file_name = "report/report_style.css"

    # Check that qa_dir and the other directories exists
    if not os.path.exists(qa_dir):
        logging.error("Directory {0:s} does not exists. Abort".format(qa_dir))
        sys.exit(-1)
    else:
        # Create directory structure for the report
        create_dir_stat = hpd.create_report_dirs(
            obs_id, qa_dir, subpages, css_file=css_file_name, js_file=js_file_name)

    print("Creating report")

    create_main_html_stat = hp.create_main_html(
        qa_dir, obs_id, subpages, css_file=css_file_name, js_file=js_file_name)

    if create_main_html_stat == 1:
        print("Creating report succesfull")
    else:
        print("ERROR: Creating report failed")

    print("Creating report. Done ({0:.0f}s)".format(time.time()-start_time))

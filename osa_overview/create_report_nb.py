# version of ../create_report to run as part of the pipeline


import os
import sys
from astropy.table import Table
import logging
import glob
import time
import argparse
import socket
from apercal.libs import lib
from dataqa.report import html_report as hp
from dataqa.report import html_report_dir as hpd
from dataqa.report.pipeline_run_time import get_pipeline_run_time
from dataqa.scandata import get_default_imagepath


def run():
    """Function to create the web report by the OSA.

    It is very similar to create_report.py with the important
    difference that it does not require any arguments from the OSA.
    This also means that this function does not work unless create_report.py
    was run as it requires the observation information file in the directory of the obs
    """

    start_time = time.time()

    # get the file name as seen from the directory of where the script will be run
    obs_file = glob.glob(
        "../[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_obs.csv")

    if len(obs_file) == 0:
        print("ERROR: No observing file found. Please make sure that the observation was processed by the QA or ask for help. Abort")
        return -1
    else:
        obs_info = Table.read(obs_file[0])

    obs_id = obs_info['Obs_ID'][0]

    # directory where the QA is
    qa_dir = get_default_imagepath(obs_id)

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

    # check if a report is available
    add_osa_report = False
    #osa_report = ''
    # # if osa report should be added, check it is available
    # if add_osa_report:
    #     # name of the osa report for this observation
    #     osa_report = os.path.join(
    #         qa_report_dir, "OSA_Report/{}_OSA_report.ecsv")

    #     # check that the file is actually there
    #     if not os.path.exists(osa_report):
    #         logger.error("No OSA report found. Abort")
    #         return -1
    # else:
    #     osa_report = ''

    # check on which happili we are:
    host_name = socket.gethostname()

    trigger_mode = False

    if host_name != "happili-01":
        logger.error(
            "You are not working on happili-01. This script will not work here. Abort")
        return -1

    # logging.basicConfig(filename='{0:s}/create_report.log'.format(qa_dir), level=logging.DEBUG,
    #                     format='%(asctime)s - %(levelname)s: %(message)s')

    # getting timing measurment for apercal
    # this could be removed and taken care of by linking to the other happili node files
    # the information is already there.
    if not add_osa_report:
        try:
            get_pipeline_run_time(obs_id, trigger_mode=trigger_mode)
        except Exception as e:
            logger.error(e)

    # the subpages to be created
    subpages = ['observing_log', 'summary', 'inspection_plots', 'preflag', 'crosscal',
                'selfcal', 'continuum', 'line', 'mosaic', 'apercal_log']

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
        if not add_osa_report:
            try:
                hpd.create_report_dirs(
                    obs_id, qa_dir, subpages, trigger_mode=trigger_mode, obs_info=obs_info)
            except Exception as e:
                logger.error(e)

    logger.info("#### Creating report")

    try:
        hp.create_main_html(qa_report_dir, obs_id, subpages,
                            css_file=css_file_name, js_file=js_file_name, obs_info=obs_info, add_osa_report=add_osa_report)
    except Exception as e:
        logger.error(e)

    logger.info("#### Report. Done ({0:.0f}s)".format(
        time.time()-start_time))

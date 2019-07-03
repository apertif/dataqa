#!/usr/bin/python2.7

"""
This file contains functionality to create the content for the
each subpage of the report
"""
import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

from html_report_content_observing_log import write_obs_content_observing_log
from html_report_content_summary import write_obs_content_summary
from html_report_content_inspection_plots import write_obs_content_inspection_plots
from html_report_content_preflag import write_obs_content_preflag
from html_report_content_crosscal import write_obs_content_crosscal
from html_report_content_selfcal import write_obs_content_selfcal
from html_report_content_continuum import write_obs_content_continuum
from html_report_content_line import write_obs_content_line
from html_report_content_mosaic import write_obs_content_mosaic
from html_report_content_apercal_logs import write_obs_content_apercal_log

logger = logging.getLogger(__name__)


def write_obs_content(page_name, qa_report_path, page_type='', obs_id='', obs_info=None, osa_report=''):
    """
    Function to write Observation content
    """

    # empty string of html code to start with
    html_code = """"""

    # html_code = """<p>NOTE: When clicking on the buttons for the first time, please click twice (small bug)</p>"""

    qa_report_obs_path = "{0:s}/{1:s}".format(qa_report_path, obs_id)

    # create html content for subpage observing_log
    # +++++++++++++++++++++++++++++++++++++++++++++
    if page_type == 'observing_log':

        try:
            html_code = write_obs_content_observing_log(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.warning("Creating content for observing log failed.")
            logger.exception(e)

    # create html content for subpage summary
    # +++++++++++++++++++++++++++++++++++++++
    if page_type == 'summary':

        try:
            html_code = write_obs_content_summary(
                html_code, qa_report_obs_path, page_type, obs_info=obs_info, osa_report=osa_report)
        except Exception as e:
            logger.warning("Creating content for summary failed.")
            logger.exception(e)

    # create html content for subpage inspection plots
    # ++++++++++++++++++++++++++++++++++++++++++++++++
    if page_type == 'inspection_plots':

        try:
            html_code = write_obs_content_inspection_plots(
                html_code, qa_report_obs_path, page_type, obs_info=obs_info)
        except Exception as e:
            logger.warning("Creating content for inspection plots failed.")
            logger.exception(e)

    # create html content for subpage preflag
    # +++++++++++++++++++++++++++++++++++++++
    if page_type == 'preflag':

        try:
            html_code = write_obs_content_preflag(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.warning("Creating content for preflag failed.")
            logger.exception(e)

    # create html content for subpage crosscal
    # ++++++++++++++++++++++++++++++++++++++++
    elif page_type == 'crosscal':

        try:
            html_code = write_obs_content_crosscal(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.warning("Creating content for crosscal failed.")
            logger.exception(e)

    # create html content for subpage selfcal
    # ++++++++++++++++++++++++++++++++++++
    elif page_type == 'selfcal':

        try:
            html_code = write_obs_content_selfcal(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.warning("Creating content for selfcal failed.")
            logger.exception(e)

    # create html content for subpage continuum
    # +++++++++++++++++++++++++++++++++++++++++
    elif page_type == 'continuum':

        try:
            html_code = write_obs_content_continuum(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.warning("Creating content for continuum failed.")
            logger.exception(e)

    # create html content for subpage line
    # ++++++++++++++++++++++++++++++++++++
    elif page_type == 'line':

        try:
            html_code = write_obs_content_line(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.warning("Creating content for line failed.")
            logger.exception(e)

    # create html content for subpage mosaic
    # ++++++++++++++++++++++++++++++++++++++
    elif page_type == 'mosaic':

        try:
            html_code = write_obs_content_mosaic(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.warning("Creating content for mosaic failed.")
            logger.exception(e)

    # create html content for subpage apercal
    # as this is a text file, it is a bit more
    # complicated and requires creating a dummy
    # html file. Otherwise, it can automatically
    # trigger the download questions
    # +++++++++++++++++++++++++++++++++++++++
    elif page_type == "apercal_log":

        try:
            html_code = write_obs_content_apercal_log(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.warning("Creating content for apercal log failed.")
            logger.exception(e)

    try:
        html_file = open(page_name, 'a')
        html_file.write(html_code)
        html_file.close()
    except Exception as e:
        logger.exception(e)
        logger.error("Writing obs content failed")
        return -1

    return 1

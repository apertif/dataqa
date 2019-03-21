#!/usr/bin/python2.7

"""
This file contains functionality to create the directory structure for the report
"""

import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
from shutil import copy

logger = logging.getLogger(__name__)


def create_report_dirs(obs_id, qa_dir, subpages, css_file='', js_file=''):
    """
    Function to create the directory structure for the
    report/html document.
    Files that are required will be linked to there.
    """

    # first check that the subdirectory report exists
    qa_dir_report = "{0:s}report".format(qa_dir)

    # copy the js and css files
    try:
        copy(js_file, "{0:s}/{1:s}".format(qa_dir_report,
                                           os.path.basename(js_file)))
    except Exception as e:
        logger.error(e)

    try:
        copy(css_file,
             "{0:s}/{1:s}".format(qa_dir_report, os.path.basename(css_file)))
    except Exception as e:
        logger.error(e)

    # create sub-directory for observation
    # not necessary, but useful if multiple reports are combined
    qa_dir_report_obs = "{0:s}/{1:s}".format(qa_dir_report, obs_id)

    if os.path.exists(qa_dir_report_obs):
        logger.info("Directory 'report' already exists")
    else:
        logger.warning(
            "Directory 'report/{0:s}' does not exists and will be created".format(obs_id))
        os.mkdir(qa_dir_report_obs)

    # go through the subpages and create the directories for them
    # also check for content and link the files
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    for page in subpages:

        qa_dir_subpage = "{0:s}/{1:s}".format(
            qa_dir_report_obs, page)

        if os.path.exists(qa_dir_subpage):
            logger.info("Directory 'report' already exists")
        else:
            logger.warning(
                "Directory 'report/{0:s}/{1:s}' does not exists and will be created".format(obs_id, page))
            os.mkdir(qa_dir_subpage)

        # Create links for files from prepare QA
        # ++++++++++++++++++++++++++++++++++++++
        if page == "prepare":

            # get beams
            beam_list = glob.glob(
                "{0:s}/{1:s}/[0-3][0-9]".format(qa_dir, page))

            # number of beams
            n_beams = len(beam_list)

            if n_beams != 0:

                beam_list.sort()

                # go through all beams
                for beam in beam_list:

                    qa_dir_subpage_prepare_beam = "{0:s}/{1:s}".format(
                        qa_dir_subpage, os.path.basename(beam))

                    # create a subdirectory in the report dir
                    try:
                        os.mkdir(qa_dir_subpage_prepare_beam)
                    except Exception as e:
                        logger.error(e)

                    # get the images in the beam directory and link them
                    images_in_beam = glob.glob("{0:s}/*png".format(beam))

                    if len(images_in_beam) != 0:

                        images_in_beam.sort()

                        for image in images_in_beam:
                            link_name = "{0:s}/{1:s}".format(
                                qa_dir_subpage_prepare_beam, os.path.basename(image))

                            # check if link exists
                            if not os.path.exists(link_name):
                                os.symlink(image, link_name)
                            else:
                                os.unlink(link_name)
                                os.symlink(image, link_name)

                    else:
                        logger.error("No images in beam {0:s} found".format(
                            beam))
            else:
                logger.error("No beams found for prepare found")

        # Create links for files from crosscal QA
        # +++++++++++++++++++++++++++++++++++++++
        elif page == "crosscal":

            # get the images in the subdirectory
            images_crosscal = glob.glob(
                "{0:s}/{1:s}/*.png".format(qa_dir, page))

            if len(images_crosscal) != 0:

                images_crosscal.sort()

                # go through all beams
                for image in images_crosscal:

                    link_name = "{0:s}/{1:s}".format(
                        qa_dir_subpage, os.path.basename(image))

                    # check if link exists
                    if not os.path.exists(link_name):
                        os.symlink(image, link_name)
                    else:
                        os.unlink(link_name)
                        os.symlink(image, link_name)

            else:
                logger.error("No images found for crosscal")

        # Create links for files from continuum QA
        # +++++++++++++++++++++++++++++++++++++++
        elif page == "continuum":

            # get beams
            beam_list = glob.glob(
                "{0:s}/{1:s}/[0-3][0-9]".format(qa_dir, page))

            # number of beams
            n_beams = len(beam_list)

            if n_beams != 0:

                beam_list.sort()

                # go through all beams
                for beam in beam_list:

                    qa_dir_subpage_prepare_beam = "{0:s}/{1:s}".format(
                        qa_dir_subpage, os.path.basename(beam))

                    # create a subdirectory in the report dir
                    try:
                        os.mkdir(qa_dir_subpage_prepare_beam)
                    except Exception as e:
                        logger.error(e)

                    # get the images in the beam directory and link them
                    images_in_beam = glob.glob(
                        "{0:s}/pybdsf/*png".format(beam))

                    if len(images_in_beam) != 0:

                        images_in_beam.sort()

                        for image in images_in_beam:
                            link_name = "{0:s}/{1:s}".format(
                                qa_dir_subpage_prepare_beam, os.path.basename(image))

                            # check if link exists
                            if not os.path.exists(link_name):
                                os.symlink(image, link_name)
                            else:
                                os.unlink(link_name)
                                os.symlink(image, link_name)
                    else:
                        logger.error("No images in beam {0:s} found".format(
                            beam))

                    # link the validation tool
                    validation_tool = "{0:s}/validation_tool".format(
                        beam)

                    # check that the directory for the validation tool exists
                    if os.path.exists(validation_tool):

                        link_name = "{0:s}/{1:s}".format(
                            qa_dir_subpage_prepare_beam, os.path.basename(validation_tool))

                        # check if link exists
                        if not os.path.exists(link_name):
                            os.symlink(validation_tool, link_name)
                        else:
                            os.unlink(link_name)
                            os.symlink(validation_tool, link_name)
                    else:
                        logger.error(
                            "No validation tool output found for continuum QA of beam {0:s}".format(beam))
            else:
                logger.error("No beams found for continuum found")

        # Create links for files from mosaic QA
        # +++++++++++++++++++++++++++++++++++++++
        elif page == "mosaic":
            # get the images in the subdirectory
            images_mosaic = glob.glob(
                "{0:s}/{1:s}/pybdsf/*.png".format(qa_dir, page))

            if len(images_mosaic) != 0:

                images_mosaic.sort()

                # go through all beams
                for image in images_mosaic:

                    link_name = "{0:s}/{1:s}".format(
                        qa_dir_subpage, os.path.basename(image))

                    # check if link exists
                    if not os.path.exists(link_name):
                        os.symlink(image, link_name)
                    else:
                        os.unlink(link_name)
                        os.symlink(image, link_name)
            else:
                logging.error("No images found for mosaic")

            # link the validation tool
            validation_tool = "{0:s}/{1:s}/validation_tool".format(
                qa_dir, page)

            # check that the directory for the validation tool exists
            if os.path.exists(validation_tool):

                link_name = "{0:s}/{1:s}".format(
                    qa_dir_subpage, os.path.basename(validation_tool))

                # check if link exists
                if not os.path.exists(link_name):
                    os.symlink(validation_tool, link_name)
                else:
                    os.unlink(link_name)
                    os.symlink(validation_tool, link_name)
            else:
                logger.error("No validation tool output found for mosaic")

        # Create links for files from aperca log
        # ++++++++++++++++++++++++++++++++++++++
        if page == "apercal_log":

            # check first on which happili we are:
            host_name = socket.gethostname()

            if host_name != "happili-01":
                logger.warning("You are not working on happili-01.")
                logger.warning("The script will not process all beams")
                logger.warning("Please switch to happili-01")
                apercal_log_file = "/data/apertif/{0:s}/apercal.log".format(
                    obs_id)

                link_name = "{0:s}/{1:s}".format(
                    qa_dir_subpage, os.path.basename(apercal_log_file))

                # rename the link to the log file according to host
                if host_name == "happili-02":
                    link_name = link_name.replace(".log", "_beam_10-19.log")
                elif host_name == "happili-03":
                    link_name = link_name.replace(".log", "_beam_20-29.log")
                elif host_name == "happili-04":
                    link_name = link_name.replace(".log", "_beam_30-39.log")

                # check if link exists
                if not os.path.exists(link_name):
                    os.symlink(image, link_name)
                else:
                    os.unlink(link_name)
                    os.symlink(image, link_name)
            # just for testing
            elif socket.gethostname() == "dop387":

                apercal_log_file = "{0:s}/apercal.log".format(qa_dir)

                link_name = "{0:s}/{1:s}".format(
                    qa_dir_subpage, os.path.basename(apercal_log_file))

                link_name = link_name.replace(".log", "_beam_00-09.log")

                # check if link exists
                if not os.path.exists(link_name):
                    os.symlink(apercal_log_file, link_name)
                else:
                    os.unlink(link_name)
                    os.symlink(apercal_log_file, link_name)
            else:
                apercal_log_file_list = [
                    "/data/apertif/{0:s}/apercal.log".format(obs_id), "/data2/apertif/{0:s}/apercal.log".format(obs_id), "/data3/apertif/{0:s}/apercal.log".format(obs_id), "/data4/apertif/{0:s}/apercal.log".format(obs_id)]

                log_file_counter = 0

                # go through the files and link them
                for apercal_log_file in apercal_log_file_list:

                    link_name = "{0:s}/{1:s}".format(
                        qa_dir_subpage, os.path.basename(apercal_log_file))

                    link_name = link_name.replace(
                        ".log", "_beam_{0:d}0-{0:d}9.log".format(log_file_counter))

                    # check if link exists
                    if not os.path.exists(link_name):
                        os.symlink(apercal_log_file, link_name)
                    else:
                        os.unlink(link_name)
                        os.symlink(apercal_log_file, link_name)

                    log_file_counter += 1

    return 1

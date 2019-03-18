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


def create_report_dirs(obs_id, qa_dir, subpages):
    """
    Function to create the directory structure for the
    report/html document.
    Files that are required will be linked to there.
    """

    # first check that the subdirectory report exists
    qa_dir_report = "{0:s}/report".format(qa_dir)

    if os.path.exists(qa_dir_report):
        logging.info("Directory 'report' already exists")
    else:
        logging.warning(
            "Directory 'report' does not exists and will be created")
        os.mkdir(qa_dir_report)

    # create sub-directory for observation
    # not necessary, but useful if multiple reports are combined
    qa_dir_report_obs = "{0:s}/{1:d}".format(qa_dir_report, obs_id)

    if os.path.exists(qa_dir_report_obs):
        logging.info("Directory 'report' already exists")
    else:
        logging.warning(
            "Directory 'report/{0:d}' does not exists and will be created".format(obs_id))
        os.mkdir(qa_dir_report_obs)

    # go through the subpages and create the directories for them
    # also check for content and link the files
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    for page in subpages:

        qa_dir_subpage = "{0:s}/{1:s}".format(
            qa_dir_report_obs, page)

        if os.path.exists(qa_dir_subpage):
            logging.info("Directory 'report' already exists")
        else:
            logging.warning(
                "Directory 'report/{0:d}/{1:s}' does not exists and will be created".format(obs_id, page))
            os.mkdir(qa_dir_subpage)

        # link the specific files for the html document
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
                        logging.error(e)

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
                        print("ERROR: No images in beam {0:s} found".format(
                            beam))
            else:
                print("ERROR: No beams found for prepare found")

        if page == "crosscal":

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
                print("ERROR: No images found for crosscal")

        if page == "apercal_log":

            # check first on which happili we are:
            host_name = socket.gethostname()

            if host_name != "happili-01":
                print("WARNING: You are not working on happili-01.")
                print("WARNING: The script will not process all beams")
                print("Please switch to happili-01")
                apercal_log_file = "/data/apertif/{0:d}/apercal.log".format(
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

            else:
                apercal_log_file_list = [
                    "/data/apertif/{0:d}/apercal.log".format(obs_id), "/data2/apertif/{0:d}/apercal.log".format(obs_id), "/data3/apertif/{0:d}/apercal.log".format(obs_id), "/data4/apertif/{0:d}/apercal.log".format(obs_id)]

                log_file_counter = 0

                # go through the files and link them
                for apercal_log_file in apercal_log_file_list:

                    link_name = "{0:s}/{1:s}".format(
                        qa_dir_subpage, os.path.basename(apercal_log_file))

                    link_name = link_name.replace(
                        ".log", "_beam_{0:d}0-{0:d}9.log".format(log_file_counter))

                    # check if link exists
                    if not os.path.exists(link_name):
                        os.symlink(image, link_name)
                    else:
                        os.unlink(link_name)
                        os.symlink(image, link_name)

                    log_file_counter += 1

            # just for testing
            if socket.gethostname() == "dop387":

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

    return 1

#!/usr/bin/python2.7

"""
This file contains functionality to create the directory structure for the report.
Instead of copying files, they are linked.
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


def create_report_dir_preflag(obs_id, qa_dir, qa_dir_report_obs_subpage, trigger_mode=False):
    """Function to create the preflag directory for the report

    Note:
        All necessary files will be linked to this directory
        from the preflag QA directory
    """

    logger.info("## Creating report directory for preflag and linking files...")

    if socket.gethostname() != 'happili-01' or trigger_mode:
        qa_preflag_dir_list = ["{0:s}preflag".format(qa_dir)]
    else:
        qa_preflag_dir_list = ["{0:s}preflag".format(qa_dir), "{0:s}preflag".format(qa_dir).replace(
            "data", "data2"), "{0:s}preflag".format(qa_dir).replace("data", "data3"), "{0:s}preflag".format(qa_dir).replace("data", "data4")]

    for qa_preflag_dir in qa_preflag_dir_list:

        # get beams
        qa_preflag_dir_beam_list = glob.glob(
            "{0:s}/[0-3][0-9]".format(qa_preflag_dir))

        # number of beams
        n_beams = len(qa_preflag_dir_beam_list)

        if n_beams != 0:

            qa_preflag_dir_beam_list.sort()

            # go through all beams
            for qa_preflag_dir_beam in qa_preflag_dir_beam_list:

                qa_dir_report_obs_subpage_preflag_beam = "{0:s}/{1:s}".format(
                    qa_dir_report_obs_subpage, os.path.basename(qa_preflag_dir_beam))

                # create a subdirectory in the report dir
                if not os.path.exists(qa_dir_report_obs_subpage_preflag_beam):
                    try:
                        os.mkdir(qa_dir_report_obs_subpage_preflag_beam)
                    except Exception as e:
                        logger.error(e)

                # get the images in the beam directory and link them
                images_in_beam = glob.glob(
                    "{0:s}/*png".format(qa_preflag_dir_beam))

                # check that there are images in there
                if len(images_in_beam) != 0:

                    images_in_beam.sort()

                    # go through the images and link them
                    for image in images_in_beam:
                        link_name = "{0:s}/{1:s}".format(
                            qa_dir_report_obs_subpage_preflag_beam, os.path.basename(image))

                        # change to relative link when in trigger mode
                        if trigger_mode:
                            image = image.replace(
                                qa_dir, "../../../../")

                        # check if link exists
                        if not os.path.exists(link_name):
                            os.symlink(image, link_name)
                        else:
                            # link needs to be removed before it can be overwritten
                            os.unlink(link_name)
                            os.symlink(image, link_name)

                else:
                    logger.warning("No images in beam {0:s} found".format(
                        qa_preflag_dir_beam))
        else:
            logger.warning(
                "No beams found for preflag QA in {0:s}".format(qa_preflag_dir))

    logger.info(
        "## Creating report directory for preflag and linking files. Done")


def create_report_dir_crosscal(qa_dir, qa_dir_report_obs_subpage, trigger_mode=False):
    """Function to create the create directory for the report

    Note:
        All necessary files will be linked to this directory
        from the crosscal QA directory
    """

    logger.info(
        "## Creating report directory for crosscal and linking files...")

    # get the images in the subdirectory
    images_crosscal = glob.glob(
        "{0:s}crosscal/*.png".format(qa_dir))

    if len(images_crosscal) != 0:

        images_crosscal.sort()

        # go through all beams
        for image in images_crosscal:

            link_name = "{0:s}/{1:s}".format(
                qa_dir_report_obs_subpage, os.path.basename(image))

            # change to relative link when in trigger mode
            if trigger_mode:
                image = image.replace(
                    qa_dir, "../../../")

            # check if link exists
            if not os.path.exists(link_name):
                os.symlink(image, link_name)
            else:
                os.unlink(link_name)
                os.symlink(image, link_name)

    else:
        logger.warning("No images found for crosscal.")

    logger.info(
        "## Creating report directory for crosscal and linking files. Done")


def create_report_dir_selfcal(qa_dir, qa_dir_report_obs_subpage, trigger_mode=False):
    """Function to create the selfcal directory for the report

    Note:
        All necessary files will be linked to this directory
        from the selfcal QA directory
    """

    logger.info(
        "## Creating report directory for selfcal and linking files...")

    # get beams
    beam_list = glob.glob(
        "{0:s}selfcal/[0-3][0-9]".format(qa_dir))

    # number of beams
    n_beams = len(beam_list)

    if n_beams != 0:

        beam_list.sort()

        # go through all beams
        for beam in beam_list:

            qa_dir_report_obs_subpage_selfcal_beam = "{0:s}/{1:s}".format(
                qa_dir_report_obs_subpage, os.path.basename(beam))

            # create a subdirectory in the report dir
            if not os.path.exists(qa_dir_report_obs_subpage_selfcal_beam):
                try:
                    os.mkdir(qa_dir_report_obs_subpage_selfcal_beam)
                except Exception as e:
                    logger.error(e)

            # get the images in the beam directory and link them
            images_in_beam = glob.glob(
                "{0:s}/*png".format(beam))

            if len(images_in_beam) != 0:

                images_in_beam.sort()

                for image in images_in_beam:
                    link_name = "{0:s}/{1:s}".format(
                        qa_dir_report_obs_subpage_selfcal_beam, os.path.basename(image))

                    # change to relative link when in trigger mode
                    if trigger_mode:
                        image = image.replace(
                            qa_dir, "../../../../")

                    # check if link exists
                    if not os.path.exists(link_name):
                        os.symlink(image, link_name)
                    else:
                        os.unlink(link_name)
                        os.symlink(image, link_name)
            else:
                logger.warning("No selfcal images in beam {0:s} found".format(
                    beam))
    else:
        logger.warning("No beams for selfcal found")

    # Get the phase plots and link them
    images_phase = glob.glob(
        "{0:s}selfcal/SCAL_phase*.png".format(qa_dir))

    if len(images_phase) != 0:

        images_phase.sort()

        # go through all antennas
        for image in images_phase:
            link_name = "{0:s}/{1:s}".format(
                qa_dir_report_obs_subpage, os.path.basename(image))

            # change to relative link when in trigger mode
            if trigger_mode:
                image = image.replace(
                    qa_dir, "../../../")

            # check if link exists
            if not os.path.exists(link_name):
                os.symlink(image, link_name)
            else:
                os.unlink(link_name)
                os.symlink(image, link_name)

    else:
        logger.warning("No selfcal phase plots found")

    # Get the amplitude plots and link them
    images_amp = glob.glob(
        "{0:s}selfcal/SCAL_amp*.png".format(qa_dir))

    if len(images_amp) != 0:

        images_amp.sort()

        # go through all antennas
        for image in images_amp:
            link_name = "{0:s}/{1:s}".format(
                qa_dir_report_obs_subpage, os.path.basename(image))

            # change to relative link when in trigger mode
            if trigger_mode:
                image = image.replace(
                    qa_dir, "../../../")

            # check if link exists
            if not os.path.exists(link_name):
                os.symlink(image, link_name)
            else:
                os.unlink(link_name)
                os.symlink(image, link_name)

    else:
        logger.warning("No selfcal amplitude plots found")

    logger.info(
        "## Creating report directory for selfcal and linking files. Done")

    # # get beams
    # beam_list = glob.glob(
    #     "{0:s}selfcal/[0-3][0-9]".format(qa_dir))

    # # number of beams
    # n_beams = len(beam_list)

    # if n_beams != 0:

    #     beam_list.sort()

    #     # go through all beams
    #     for beam in beam_list:

    #         qa_dir_report_obs_subpage_line_beam = "{0:s}/{1:s}".format(
    #             qa_dir_report_obs_subpage, os.path.basename(beam))

    #         # create a subdirectory in the report dir
    #         try:
    #             os.mkdir(qa_dir_report_obs_subpage_line_beam)
    #         except Exception as e:
    #             logger.error(e)

    #         # get the images in the beam directory and link them
    #         images_in_beam = glob.glob(
    #             "{0:s}/*png".format(beam))

    #         if len(images_in_beam) != 0:

    #             images_in_beam.sort()

    #             for image in images_in_beam:
    #                 link_name = "{0:s}/{1:s}".format(
    #                     qa_dir_report_obs_subpage_line_beam, os.path.basename(image))

    #                 # check if link exists
    #                 if not os.path.exists(link_name):
    #                     os.symlink(image, link_name)
    #                 else:
    #                     os.unlink(link_name)
    #                     os.symlink(image, link_name)
    #         else:
    #             logger.warning("No images in beam {0:s} found".format(
    #                 beam))
    # else:
    #     logger.warning("No beams found for selfcal found")
#
#    logger.info(
#        "## Creating report directory for selfcal and linking files. Done")


def create_report_dir_continuum(qa_dir, qa_dir_report_obs_subpage, trigger_mode=False):
    """Function to create the continuum directory for the report

    Note:
        All necessary files will be linked to this directory
        from the continuum QA directory
    """

    logger.info(
        "## Creating report directory for continuum and linking files...")

    # get beams
    beam_list = glob.glob(
        "{0:s}continuum/[0-3][0-9]".format(qa_dir))

    # number of beams
    n_beams = len(beam_list)

    if n_beams != 0:

        beam_list.sort()

        # go through all beams
        for beam in beam_list:

            qa_dir_report_obs_subpage_continuum_beam = "{0:s}/{1:s}".format(
                qa_dir_report_obs_subpage, os.path.basename(beam))

            # create a subdirectory in the report dir
            if not os.path.exists(qa_dir_report_obs_subpage_continuum_beam):
                try:
                    os.mkdir(qa_dir_report_obs_subpage_continuum_beam)
                except Exception as e:
                    logger.error(e)

            # get the images in the beam directory and link them
            images_in_beam = glob.glob(
                "{0:s}/*png".format(beam))

            if len(images_in_beam) != 0:

                images_in_beam.sort()

                for image in images_in_beam:
                    link_name = "{0:s}/{1:s}".format(
                        qa_dir_report_obs_subpage_continuum_beam, os.path.basename(image))

                    # change to relative link when in trigger mode
                    if trigger_mode:
                        image = image.replace(
                            qa_dir, "../../../../")

                    # check if link exists
                    if not os.path.exists(link_name):
                        os.symlink(image, link_name)
                    else:
                        os.unlink(link_name)
                        os.symlink(image, link_name)
            else:
                logger.warning("No images in beam {0:s} found".format(
                    beam))

            # link the validation tool
            validation_tool_dir = glob.glob("{0:s}/*continuum_validation_pybdsf_snr5.0_int".format(
                beam))

            # check that the directory for the validation tool exists
            if len(validation_tool_dir) == 1:
                validation_tool_dir = validation_tool_dir[0]

                if os.path.isdir(validation_tool_dir):

                    link_name = "{0:s}/{1:s}".format(
                        qa_dir_report_obs_subpage_continuum_beam, os.path.basename(validation_tool_dir))

                    # change to relative link when in trigger mode
                    if trigger_mode:
                        validation_tool_dir = validation_tool_dir.replace(
                            qa_dir, "../../../../")

                    # check if link exists
                    if not os.path.exists(link_name):
                        os.symlink(validation_tool_dir, link_name)
                    else:
                        os.unlink(link_name)
                        os.symlink(validation_tool_dir, link_name)
                else:
                    logger.warning(
                        "No validation tool output found for continuum QA of beam {0:s}".format(beam))
            else:
                logger.warning(
                    "No validation tool output found for continuum QA of beam {0:s}".format(beam))
    else:
        logger.warning("No beams found for continuum found")

    logger.info(
        "## Creating report directory for continuum and linking files. Done")


def create_report_dir_line(qa_dir, qa_dir_report_obs_subpage, trigger_mode=False):
    """Function to create the line directory for the report

    Note:
        All necessary files will be linked to this directory
        from the line QA directory
    """

    logger.info(
        "## Creating report directory for line and linking files...")

    # get beams
    beam_list = glob.glob(
        "{0:s}line/[0-3][0-9]".format(qa_dir))

    # number of beams
    n_beams = len(beam_list)

    if n_beams != 0:

        beam_list.sort()

        # go through all beams
        for beam in beam_list:

            qa_dir_report_obs_subpage_line_beam = "{0:s}/{1:s}".format(
                qa_dir_report_obs_subpage, os.path.basename(beam))

            # create a subdirectory in the report dir
            if not os.path.exists(qa_dir_report_obs_subpage_line_beam):
                try:
                    os.mkdir(qa_dir_report_obs_subpage_line_beam)
                except Exception as e:
                    logger.error(e)

            # get the images in the beam directory and link them
            images_in_beam = glob.glob(
                "{0:s}/*png".format(beam))

            if len(images_in_beam) != 0:

                images_in_beam.sort()

                for image in images_in_beam:
                    link_name = "{0:s}/{1:s}".format(
                        qa_dir_report_obs_subpage_line_beam, os.path.basename(image))

                    # change to relative link when in trigger mode
                    if trigger_mode:
                        image = image.replace(
                            qa_dir, "../../../../")

                    # check if link exists
                    if not os.path.exists(link_name):
                        os.symlink(image, link_name)
                    else:
                        os.unlink(link_name)
                        os.symlink(image, link_name)
            else:
                logger.warning("No images in beam {0:s} found".format(
                    beam))
    else:
        logger.warning("No beams found for line found")

    logger.info(
        "## Creating report directory for line and linking files. Done")


def create_report_dir_mosaic(qa_dir, qa_dir_report_obs_subpage, trigger_mode=False):
    """Function to create the mosaic directory for the report

    Note:
        All necessary files will be linked to this directory
        from the mosaic QA directory
    """

    logger.info(
        "## Creating report directory for mosaic and linking files...")

    qa_mosaic_dir = "{0:s}mosaic".format(qa_dir)

    # get the images in the subdirectory
    images_mosaic = glob.glob("{0:s}/*.png".format(qa_mosaic_dir))

    if len(images_mosaic) != 0:

        images_mosaic.sort()

        # go through all beams
        for image in images_mosaic:

            link_name = "{0:s}/{1:s}".format(
                qa_dir_report_obs_subpage, os.path.basename(image))

            # change to relative link when in trigger mode
            if trigger_mode:
                image = image.replace(
                    qa_dir, "../../../moasic/")

            # check if link exists
            if not os.path.exists(link_name):
                os.symlink(image, link_name)
            else:
                os.unlink(link_name)
                os.symlink(image, link_name)
    else:
        logging.warning("No images found for mosaic")

    # link the validation tool
    validation_tool_dir = glob.glob("{0:s}/*continuum_validation_pybdsf_snr5.0_int".format(
        qa_mosaic_dir))

    # check that the directory for the validation tool exists
    if len(validation_tool_dir) == 1:
        validation_tool_dir = validation_tool_dir[0]

        if os.path.isdir(validation_tool_dir):

            link_name = "{0:s}/{1:s}".format(
                qa_dir_report_obs_subpage, os.path.basename(validation_tool_dir))

            # change to relative link when in trigger mode
            if trigger_mode:
                validation_tool_dir = validation_tool_dir.replace(
                    qa_dir, "../../../")

            # check if link exists
            if not os.path.exists(link_name):
                os.symlink(validation_tool_dir, link_name)
            else:
                os.unlink(link_name)
                os.symlink(validation_tool_dir, link_name)
        else:
            logger.warning("No validation tool output found for mosaic")
    else:
        logger.warning("No validation tool output found for mosaic")

    logger.info(
        "## Creating report directory for mosaic and linking files. Done")


def create_report_dir_apercal_log(qa_dir, qa_dir_report_obs_subpage, trigger_mode=False):
    """Function to create the apercal log directory for the report

    Note:
        All four apercal.log file will be linked to this directory, but
        for better processing they will be renamed to .txt files
    """

    logger.info(
        "## Creating report directory for apercal log and linking files...")

    # check first on which happili we are:
    host_name = socket.gethostname()

    # this one does not take parallelisation into account
    # only the code for running it on happili-01 does
    if host_name != "happili-01" or trigger_mode:

        logger.warning(
            "Cannot account for parallalized log files unless running from happili-01 !!!")

        # change to relative link when in trigger mode
        
        apercal_log_file = qa_dir.replace("qa/", "apercal.log")

        link_name = "{0:s}/{1:s}".format(
            qa_dir_report_obs_subpage, os.path.basename(apercal_log_file))

        if os.path.exists(apercal_log_file):

            if trigger_mode:
                apercal_log_file = apercal_log_file.replace(qa_dir.repalce("qa/",""),"../../../../../")

            # rename the link to the log file according to host
            if host_name == "happili-02":
                link_name = link_name.replace(
                    ".log", "_log_{0:s}.txt".format(host_name))
            elif host_name == "happili-03":
                link_name = link_name.replace(
                    ".log", "_log_{0:s}.txt".format(host_name))
            elif host_name == "happili-04":
                link_name = link_name.replace(
                    ".log", "_log_{0:s}.txt".format(host_name))

            # check if link exists
            if not os.path.exists(link_name):
                os.symlink(apercal_log_file, link_name)
            else:
                os.unlink(link_name)
                os.symlink(apercal_log_file, link_name)
        else:
            logger.warning("Could not find {0:s}".format(apercal_log_file))
    else:
        # apercal_log_file_list = [
        #     qa_dir.replace("qa/","apercal.log"), qa_dir.replace("qa/","apercal.log").replace("data", "data2"), qa_dir.replace("qa/","apercal.log").replace("data", "data3"), qa_dir.replace("qa/","apercal.log").replace("data", "data4")]

        # get the data directories
        data_dir_search_name = qa_dir.split(
            "qa/")[0].replace("/data", "/data*")
        data_dir_list = glob.glob(data_dir_search_name)

        if len(data_dir_list) != 0:

            data_dir_list.sort()

            # go through the data directories
            for dir_counter in range(len(data_dir_list)):

                # get the logfile for this data directory
                apercal_log_file_list = glob.glob(
                    "{0:s}apercal*.log".format(data_dir_list[dir_counter]))

                if len(apercal_log_file_list):

                    apercal_log_file_list.sort()

                    # go through the log file list
                    for log_file in apercal_log_file_list:

                        link_name = "{0:s}/{1:s}".format(
                            qa_dir_report_obs_subpage, os.path.basename(log_file))

                        link_name = link_name.replace(
                            ".log", "_log_happili-{0:02d}.txt".format(dir_counter+1))

                        # check if link exists
                        if not os.path.exists(link_name):
                            os.symlink(log_file, link_name)
                        else:
                            os.unlink(link_name)
                            os.symlink(log_file, link_name)
                else:
                    logger.warning("Could not find any log files in {0:s}".format(
                        data_dir_list[dir_counter]))
        else:
            logger.warning("Did not fine any data directories in {0:s}".format(
                data_dir_search_name))

    # link the timing measurement files
    apercal_timeinfo_files = glob.glob(
        "{0:s}apercal_performance/*.csv".format(qa_dir))

    if len(apercal_timeinfo_files) != 0:

        # go through list and link files
        for time_file in apercal_timeinfo_files:

            link_name = "{0:s}/{1:s}".format(
                qa_dir_report_obs_subpage, os.path.basename(time_file))

            # change to relative link when in trigger mode
            if trigger_mode:
                time_file = time_file.replace(
                    qa_dir, "../../../")

            # check if link exists
            if not os.path.exists(link_name):
                os.symlink(time_file, link_name)
            else:
                os.unlink(link_name)
                os.symlink(time_file, link_name)
    else:
        logger.warning(
            "Did not fine time measurement files in {0:s}apercal_performance/".format(qa_dir))

    logger.info(
        "## Creating report directory for apercal log and linking files. Done")


def create_report_dirs(obs_id, qa_dir, subpages, css_file='', js_file='', trigger_mode=False):
    """Function to create the directory structure of the report document

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

        qa_dir_report_obs_subpage = "{0:s}/{1:s}".format(
            qa_dir_report_obs, page)

        if os.path.exists(qa_dir_report_obs_subpage):
            logger.info("Directory 'report' already exists")
        else:
            logger.info(
                "Directory '{0:s} does not exists and will be created".format(qa_dir_report_obs_subpage))
            os.mkdir(qa_dir_report_obs_subpage)

        # Create links for files from preflag QA
        # ++++++++++++++++++++++++++++++++++++++
        if page == "preflag":

            try:
                create_report_dir_preflag(
                    obs_id, qa_dir, qa_dir_report_obs_subpage, trigger_mode=trigger_mode)
            except Exception as e:
                logger.error(e)

        # Create links for files from crosscal QA
        # +++++++++++++++++++++++++++++++++++++++
        elif page == "crosscal":

            try:
                create_report_dir_crosscal(
                    qa_dir, qa_dir_report_obs_subpage, trigger_mode=trigger_mode)
            except Exception as e:
                logger.error(e)

        # Create links for files from crosscal QA
        # +++++++++++++++++++++++++++++++++++++++
        elif page == "selfcal":

            try:
                create_report_dir_selfcal(
                    qa_dir, qa_dir_report_obs_subpage, trigger_mode=trigger_mode)
            except Exception as e:
                logger.error(e)

        # Create links for files from continuum QA
        # +++++++++++++++++++++++++++++++++++++++
        elif page == "continuum":

            try:
                create_report_dir_continuum(
                    qa_dir, qa_dir_report_obs_subpage, trigger_mode=trigger_mode)
            except Exception as e:
                logger.error(e)

        # Create links for files from line QA
        # +++++++++++++++++++++++++++++++++++++++
        elif page == "line":

            try:
                create_report_dir_line(
                    qa_dir, qa_dir_report_obs_subpage, trigger_mode=trigger_mode)
            except Exception as e:
                logger.error(e)

        # Create links for files from mosaic QA
        # +++++++++++++++++++++++++++++++++++++++
        elif page == "mosaic":

            try:
                create_report_dir_mosaic(
                    qa_dir, qa_dir_report_obs_subpage, trigger_mode=trigger_mode)
            except Exception as e:
                logger.error(e)

        # Create links for files from aperca log
        # ++++++++++++++++++++++++++++++++++++++
        if page == "apercal_log":

            try:
                create_report_dir_apercal_log(
                    qa_dir, qa_dir_report_obs_subpage, trigger_mode=trigger_mode)
            except Exception as e:
                logger.error(e)

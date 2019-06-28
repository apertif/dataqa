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


def create_report_dir_observing_log(qa_dir, qa_dir_report_obs_subpage, trigger_mode=False):
    """Function to create the observing log  for the report

    Note:
        All necessary files will be linked to this directory
        from the observing log QA directory

    Args:
        qa_dir (str): Directory of the QA
        qa_dir_report_obs_subpage (str): Directory of the subpage
        trigger_mode (bool): Set for when automatically run after Apercal on a single node
    """

    logger.info(
        "## Creating report directory for observing logs. No files to link yet")

    # # get the images in the subdirectory
    # images_inspection_plots = glob.glob(
    #     os.path.join(qa_dir, "inspection_plots/*.png"))

    # if len(images_inspection_plots) != 0:

    #     images_inspection_plots.sort()

    #     # go through all beams
    #     for image in images_inspection_plots:

    #         link_name = "{0:s}/{1:s}".format(
    #             qa_dir_report_obs_subpage, os.path.basename(image))

    #         # change to relative link when in trigger mode
    #         if trigger_mode:
    #             image = image.replace(
    #                 qa_dir, "../../../")

    #         # check if link exists
    #         if not os.path.exists(link_name):
    #             os.symlink(image, link_name)
    #         else:
    #             os.unlink(link_name)
    #             os.symlink(image, link_name)

    # else:
    #     logger.warning("No images found for inspection plots.")

    # logger.info(
    #     "## Creating report directory for inspection plots and linking files. Done")


def create_report_dir_inspection_plots(qa_dir, qa_dir_report_obs_subpage, trigger_mode=False, obs_info=None):
    """Function to create the inspection plot directory for the report

    Note:
        All necessary files will be linked to this directory
        from the inspection plot QA directory.
        It is not necessary to add the combine-parameter, because
        the inspection plots are only created on happili-01 unless ran manually.

    Args:
        qa_dir (str): Directory of the QA
        qa_dir_report_obs_subpage (str): Directory of the subpage
        trigger_mode (bool): Set for when automatically run after Apercal on a single node
        obs_info (dict): Information about the observation such as the source names
    """

    logger.info(
        "## Creating report directory for inspection plots and linking files...")

    # get the images in the subdirectory
    # without the additional obs information assume that the files are in the main dir
    if obs_info is None:

        logger.warning("No observing information provided. Will assume plots are in main directory")

        images_inspection_plots = glob.glob(
            os.path.join(qa_dir, "inspection_plots/*.png"))

        if len(images_inspection_plots) != 0:

            images_inspection_plots.sort()

            # go through all beams
            for image in images_inspection_plots:

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
            logger.warning("No images found for inspection plots.")
    # otherwise go through the sources to get the info
    else:
        default_qa_plot_dir = os.path.join(qa_dir, "inspection_plots")

        if obs_info['Pol_Calibrator'][0] != '':
            src_list = [obs_info['Target'][0], obs_info['Flux_Calibrator']
                [0], obs_info['Pol_Calibrator'][0]]
        else:
            src_list = [obs_info['Target'][0], obs_info['Flux_Calibrator'][0]]

        # go through each of the sources
        for src in src_list:

            # this is necessary as plots for the calibrator are per beam
            # and will be distributed among the different nodes
            if socket.gethostname() != 'happili-01' or trigger_mode :
                qa_plot_dir_list = [default_qa_plot_dir]
            # only check in one dir for the target plots
            elif src == obs_info['Target'][0]:
                qa_plot_dir_list = [default_qa_plot_dir]
            else:
                qa_plot_dir_list = [default_qa_plot_dir, default_qa_plot_dir.replace(
                    "data", "data2"), default_qa_plot_dir.replace("data", "data3"), default_qa_plot_dir.replace("data", "data4")]

            # now go through each of the plot directories from the differen nodes
            for qa_plot_dir in qa_plot_dir_list:

                # set the source directory in the inspection plot dir
                qa_plot_dir_src = os.path.join(
                    qa_plot_dir, "{}".format(src))

                # set the source directory where the link should be
                qa_dir_report_obs_subpage_src = os.path.join(
                    qa_dir_report_obs_subpage, src)
                # create it if it does not exists
                if not os.path.exists(qa_dir_report_obs_subpage_src):
                    os.mkdir(qa_dir_report_obs_subpage_src)

                # if it is the target the situation is simple
                # as all plots will be in one place
                if src == obs_info['Target'][0]:

                    # now get the images
                    images_inspection_plots = glob.glob(
                        os.path.join(qa_plot_dir_src, "*.png"))

                    if len(images_inspection_plots) != 0:

                        images_inspection_plots.sort()

                        # go through all beams
                        for image in images_inspection_plots:

                            link_name = "{0:s}/{1:s}".format(
                                qa_dir_report_obs_subpage_src, os.path.basename(image))

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
                            logger.warning(
                                "No images found for inspection plots for target {}.".format(src))
                # for the calibrators
                # they are separated by beam    
                else:
                    # get the beams
                    qa_plot_dir_src_beam_list = glob.glob(os.path.join(qa_plot_dir_src, "[0-3][0-9]"))

                    # check that there are actually beams
                    if len(qa_plot_dir_src_beam_list) != 0:

                        # go through the beams:
                        for qa_plot_dir_src_beam in qa_plot_dir_src_beam_list:

                            # now get the images
                            images_inspection_plots = glob.glob(
                                os.path.join(qa_plot_dir_src_beam, "*.png"))

                            # continue only if there are images in the beam dir
                            if len(images_inspection_plots) != 0:

                                # set the beam directory where the link should be
                                qa_dir_report_obs_subpage_src_beam = os.path.join(
                                    qa_dir_report_obs_subpage_src, os.path.basename(qa_plot_dir_src_beam))
                                # create it if it does not exists
                                if not os.path.exists(qa_dir_report_obs_subpage_src):
                                    os.mkdir(qa_dir_report_obs_subpage_src)

                                # go through all images and link them
                                for image in images_inspection_plots:

                                    link_name="{0:s}/{1:s}".format(
                                        qa_dir_report_obs_subpage_src_beam, os.path.basename(image))

                                    # change to relative link when in trigger mode
                                    if trigger_mode:
                                        image=image.replace(
                                            qa_dir, "../../../../../")

                                    # check if link exists
                                    if not os.path.exists(link_name):
                                        os.symlink(image, link_name)
                                    else:
                                        os.unlink(link_name)
                                        os.symlink(image, link_name)

                            else:
                                logger.warning("No images found for inspection plots for calibrator {}.".format(src))
                    else:
                        logger.warning("No beam directories found for calibrator {}".format(src))
    logger.info(
        "## Creating report directory for inspection plots and linking files. Done")

def create_report_dir_preflag(obs_id, qa_dir, qa_dir_report_obs_subpage, trigger_mode = False):
    """Function to create the preflag directory for the report

    Note:
        All necessary files will be linked to this directory
        from the preflag QA directory.
        It is not necessary to add the combine-parameter, because
        the preflag files are already distributed among the nodes.

    Args:
        qa_dir (str): Directory of the QA
        qa_dir_report_obs_subpage (str): Directory of the subpage
        trigger_mode (bool): Set for when automatically run after Apercal on a single node

    """

    logger.info("## Creating report directory for preflag and linking files...")

    default_qa_preflag_dir=os.path.join(qa_dir, "preflag")

    if socket.gethostname() != 'happili-01' or trigger_mode:
        qa_preflag_dir_list=[default_qa_preflag_dir]
    else:
        qa_preflag_dir_list=[default_qa_preflag_dir, default_qa_preflag_dir.replace(
            "data", "data2"), default_qa_preflag_dir.replace("data", "data3"), default_qa_preflag_dir.replace("data", "data4")]

    # Get the combined preflag plots when on happili-01
    # =================================================
    if socket.gethostname() == 'happili-01':
        logger.info("Linking combined preflag plots")
        # get the images in the subdirectory
        images_preflag_combined=glob.glob(
            os.path.join(default_qa_preflag_dir, "*.png"))

        if len(images_preflag_combined) != 0:

            images_preflag_combined.sort()

            # go through all beams
            for image in images_preflag_combined:

                link_name="{0:s}/{1:s}".format(
                    qa_dir_report_obs_subpage, os.path.basename(image))

                # change to relative link when in trigger mode
                if trigger_mode:
                    image=image.replace(
                        qa_dir, "../../../")

                # check if link exists
                if not os.path.exists(link_name):
                    os.symlink(image, link_name)
                else:
                    os.unlink(link_name)
                    os.symlink(image, link_name)

        else:
            logger.warning("No images found for combined preflag plots.")

    # Get every single preflag plot
    # =============================
    logger.info("Linking individual preflag plots")

    for qa_preflag_dir in qa_preflag_dir_list:

        # get beams
        qa_preflag_dir_beam_list=glob.glob(
            "{0:s}/[0-3][0-9]".format(qa_preflag_dir))

        # number of beams
        n_beams=len(qa_preflag_dir_beam_list)

        if n_beams != 0:

            qa_preflag_dir_beam_list.sort()

            # go through all beams
            for qa_preflag_dir_beam in qa_preflag_dir_beam_list:

                qa_dir_report_obs_subpage_preflag_beam="{0:s}/{1:s}".format(
                    qa_dir_report_obs_subpage, os.path.basename(qa_preflag_dir_beam))

                # create a subdirectory in the report dir
                if not os.path.exists(qa_dir_report_obs_subpage_preflag_beam):
                    try:
                        os.mkdir(qa_dir_report_obs_subpage_preflag_beam)
                    except Exception as e:
                        logger.error(e)

                # get the images in the beam directory and link them
                images_in_beam=glob.glob(
                    "{0:s}/*png".format(qa_preflag_dir_beam))

                # check that there are images in there
                if len(images_in_beam) != 0:

                    images_in_beam.sort()

                    # go through the images and link them
                    for image in images_in_beam:
                        link_name="{0:s}/{1:s}".format(
                            qa_dir_report_obs_subpage_preflag_beam, os.path.basename(image))

                        # change to relative link when in trigger mode
                        if trigger_mode:
                            image=image.replace(
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


def create_report_dir_crosscal(qa_dir, qa_dir_report_obs_subpage, trigger_mode=False, do_combine=False):
    """Function to create the create directory for the report

    Note:
        All necessary files will be linked to this directory
        from the crosscal QA directory.
    
    Args:
        qa_dir (str): Directory of the QA
        qa_dir_report_obs_subpage (str): Directory of the subpage
        trigger_mode (bool): Set for when automatically run after Apercal on a single node
        do_combine (bool): Set to combine the QA information from different happilis
    """

    logger.info(
        "## Creating report directory for crosscal and linking files...")
    
    qa_crosscal_dir = os.path.join(qa_dir,"crosscal")

    # if crosscal from different happilis should be combined
    if do_combine:
        pass
        # combine images
        # try:
        #     logging.info("Combining crosscal plots")
        #     run_merge_plots(qa_crosscal_dir, do_ccal=True, do_scal=False):
        # except Exception as e:
        #     logger.warning("Combining crosscal plots failed")
        #     logger.exception(e)
        # else:
        #     logger.info("Combining crosscal plots ... Done")
    
    # get the images for crosscal
    images_crosscal = glob.glob(
        "{0:s}/*.png".format(qa_crosscal_dir))

    # if there are any link them.
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


def create_report_dir_selfcal(qa_dir, qa_dir_report_obs_subpage, trigger_mode=False, do_combine=False):
    """Function to create the selfcal directory for the report

    Note:
        All necessary files will be linked to this directory
        from the selfcal QA directory.
    
    Args:
        qa_dir (str): Directory of the QA
        qa_dir_report_obs_subpage (str): Directory of the subpage
        trigger_mode (bool): Set for when automatically run after Apercal on a single node
        do_combine (bool): Set to combine the QA information from different happilis
    """

    default_qa_selfcal_dir = os.path.join(qa_dir, "selfcal")

    # if crosscal from different happilis should be combined
    # ======================================================
    if do_combine:
        pass
        # combine images
        # try:
        #     logging.info("Combining crosscal plots")
        #     run_merge_plots(default_qa_selfcal_dir, do_ccal=False, do_scal=True):
        # except Exception as e:
        #     logger.warning("Combining crosscal plots failed")
        #     logger.exception(e)
        # else:
        #     logger.info("Combining crosscal plots ... Done")

    logger.info(
        "## Creating report directory for selfcal and linking files...")


    # Getting selfcal images
    # ======================
    if socket.gethostname() != 'happili-01' or trigger_mode:
        qa_selfcal_dir_list = [default_qa_selfcal_dir]
    else:
        qa_selfcal_dir_list = [default_qa_selfcal_dir, default_qa_selfcal_dir.replace(
            "data", "data2"), default_qa_selfcal_dir.replace("data", "data3"), default_qa_selfcal_dir.replace("data", "data4")]

    for qa_selfcal_dir in qa_selfcal_dir_list:

        # get beams
        beam_list = glob.glob(
            "{0:s}/[0-3][0-9]".format(qa_selfcal_dir))

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
    # =================================
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
    # =====================================
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
        from the continuum QA directory.
        No need to addd combine parameter as it will try to look
        into all happili nodes.
    
    Args:
        qa_dir (str): Directory of the QA
        qa_dir_report_obs_subpage (str): Directory of the subpage
        trigger_mode (bool): Set for when automatically run after Apercal on a single node
    
    """

    logger.info(
        "## Creating report directory for continuum and linking files...")

    # Getting continuum images
    # ======================

    default_qa_continuum_dir = os.path.join(qa_dir, "continuum")

    if socket.gethostname() != 'happili-01' or trigger_mode:
        qa_continuum_dir_list = [default_qa_continuum_dir]
    else:
        qa_continuum_dir_list = [default_qa_continuum_dir, default_qa_continuum_dir.replace(
            "data", "data2"), default_qa_continuum_dir.replace("data", "data3"), default_qa_continuum_dir.replace("data", "data4")]

    for qa_continuum_dir in qa_continuum_dir_list:

        # get beams
        beam_list = glob.glob(
            "{0:s}/[0-3][0-9]".format(qa_continuum_dir))

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
        from the line QA directory.
    
    Args:
        qa_dir (str): Directory of the QA
        qa_dir_report_obs_subpage (str): Directory of the subpage
        trigger_mode (bool): Set for when automatically run after Apercal on a single node
    
    """

    logger.info(
        "## Creating report directory for line and linking files...")

    # Getting line images
    # ===================

    default_qa_line_dir = os.path.join(qa_dir, "line")

    if socket.gethostname() != 'happili-01' or trigger_mode:
        qa_line_dir_list = [default_qa_line_dir]
    else:
        qa_line_dir_list = [default_qa_line_dir, default_qa_line_dir.replace(
            "data", "data2"), default_qa_line_dir.replace("data", "data3"), default_qa_line_dir.replace("data", "data4")]

    for qa_line_dir in qa_line_dir_list:

        # get beams
        beam_list = glob.glob(
            "{0:s}/[0-3][0-9]".format(qa_line_dir))

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
        from the mosaic QA directory.
    
    Args:
        qa_dir (str): Directory of the QA
        qa_dir_report_obs_subpage (str): Directory of the subpage
        trigger_mode (bool): Set for when automatically run after Apercal on a single node
    
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
        for better processing they will be renamed to .txt files.
        This function already collects information from different 
        happilis.
    
    Args:
        qa_dir (str): Directory of the QA
        qa_dir_report_obs_subpage (str): Directory of the subpage
        trigger_mode (bool): Set for when automatically run after Apercal on a single node
    
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
                apercal_log_file = apercal_log_file.replace(qa_dir.replace("qa/",""),"../../../../")

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


def create_report_dirs(obs_id, qa_dir, subpages, css_file='', js_file='', trigger_mode=False, do_combine=False, obs_info=None):
    """Function to create the directory structure of the report document

    Files that are required will be linked to there.

    The function can create the directory for the pages:
    summary, inspection plots, preflag, crosscal, selfcal, continuum,
    line, mosaic and apercal log.

    The option to combine QA information from different happilis does not
    do anything with inspection plots and preflag. The former is only available
    from happili-01 in triggered mode and the latter is already distributed.

    Args:
        obs_id (str): ID of observation (scan/task_id)
        qa_dir (str): Directory of QA
        subpages (list(str)): List of pages to be created
        css_file (str): Path to local css file (deprecated as w3css is now used)
        js_file (str): Path to javascript file
        trigger_mode (bool): In trigger mode the report is created only for the data on the given happili
        do_combine (bool): Combine the information from different happilis.
        obs_info (dict): Additional information about the observation (target name, fluxcal, and polcal)
    """

    # first check that the subdirectory report exists
    qa_dir_report = os.path.join(qa_dir,"report")

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
            logger.info("Directory {0:s} already exists".format(qa_dir_report_obs_subpage))
        else:
            logger.info(
                "Directory '{0:s} does not exists and will be created".format(qa_dir_report_obs_subpage))
            os.mkdir(qa_dir_report_obs_subpage)

        # Create links for files from Observation log
        # +++++++++++++++++++++++++++++++++++++++++++++++
        if page == "observing_log":

            try:
                create_report_dir_observing_log(
                    qa_dir, qa_dir_report_obs_subpage, trigger_mode=trigger_mode)
            except Exception as e:
                logger.error(e)

        # Create links for files from inspection plot QA
        # +++++++++++++++++++++++++++++++++++++++++++++++
        if page == "inspection_plots":

            try:
                create_report_dir_inspection_plots(qa_dir, qa_dir_report_obs_subpage, trigger_mode=trigger_mode, obs_info=obs_info)
            except Exception as e:
                logger.error(e)

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
                    qa_dir, qa_dir_report_obs_subpage, trigger_mode=trigger_mode, do_combine=do_combine)
            except Exception as e:
                logger.error(e)

        # Create links for files from selfcal QA
        # +++++++++++++++++++++++++++++++++++++++
        elif page == "selfcal":

            try:
                create_report_dir_selfcal(
                    qa_dir, qa_dir_report_obs_subpage, trigger_mode=trigger_mode, do_combine=do_combine)
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

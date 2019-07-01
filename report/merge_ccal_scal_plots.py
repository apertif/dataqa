from dataqa.scandata import get_default_imagepath
import argparse
import time
import logging
import os
import glob
import socket
import numpy as np
from PIL import Image
from apercal.libs import lib
from apercal.subs.managefiles import director
from time import time
import pymp

logger = logging.getLogger(__name__)


def merge_plots(image_list, new_image_name=None):
    """This function does the actual merging

    Args:
        image_list (list(str)): List of images to merge with full path
        new_image_name (str): Optional name of new image
    """

    # name of the new image
    # =====================
    if new_image_name is None:
        # will most likely overwrite the existing image
        new_image_name = image_list[0]

        # check that the new image will be saved in /data/
        if new_image_name.split("/")[1] != "data":
            new_image_name = new_image_name.replace(
                new_image_name.split("/")[1], "data")

    # now go through the images and overlay them
    # ==========================================
    for k in range(len(image_list)):

        # the first image will be the background
        if k == 0:
            background = Image.open(image_list[k])
            background = background.convert("RGBA")
        else:
            overlay = Image.open(image_list[k])
            overlay = overlay.convert("RGBA")

            # get the image data of the overlay
            overlay_data = overlay.load()

            # get size of image
            img_width, img_height = overlay.size

            # go through the pixels and make the white ones transparent
            for x_pix in range(img_width):
                for y_pix in range(img_height):
                    if overlay_data[x_pix, y_pix] == (255, 255, 255, 255):
                        overlay_data[x_pix, y_pix] = (255, 255, 255, 0)

        # create a new image and merge it with background
        if k == 0:
            new_image = Image.new("RGBA", background.size)
            new_image = Image.alpha_composite(new_image, background)
        else:
            new_image = Image.alpha_composite(new_image, overlay)

    # save the merged image
    new_image.save(new_image_name, "PNG")


def run_merge_plots(qa_dir, do_ccal=True, do_scal=True, do_backup=True, run_parallel=False):
    """ This function merges the crosscal and/or selfcal plots
    that are split by beam from the different data directories.

    Args:
        qa_dir (str): Directory of QA
        do_ccal (bool): Set to merge crosscal plots (default: True)
        do_scal (bool): Set to merge selfcal plots (default: True)
    """

    # Basic settings
    # ==============

    # get the host name
    host_name = socket.gethostname()

    # start time
    start_time = time()

    # it does not make sense to run this script from another happili node
    if host_name != "happili-01":
        logger.error(
            "You are not on happili-01. This script will not work here. Abort")
        return -1

    # set whether both crosscal and selfcal plot shave to be merged or only one
    if not do_ccal and not do_scal:
        do_ccal = True
        do_scal = True
        logger.info("Merging crosscal and selfcal plots")
    elif do_ccal and not do_scal:
        logger.info("Merging only crosscal plots")
    elif not do_ccal and do_scal:
        logger.info("Merging only selfcal plots")

    # Merge the crosscal plots
    # ========================
    if do_ccal:

        qa_dir_crosscal = os.path.join(qa_dir, "crosscal")

        logger.info("## Merging crosscal plots in {}".format(qa_dir_crosscal))

        # create a backup of the original files
        if do_backup:
            # final path of backup
            qa_dir_crosscal_backup = os.path.join(
                qa_dir_crosscal, "crosscal_backup")

            # temporary path of backup for copying
            qa_dir_crosscal_backup_tmp = "{}_backup".format(qa_dir_crosscal)

            if os.path.exists(qa_dir_crosscal_backup):
                logger.info("Backup of crosscal plots already exists")
            else:
                # copy the original directory
                lib.basher("cp -r " + qa_dir_crosscal +
                           " " + qa_dir_crosscal_backup_tmp)

                # move the directory
                lib.basher("mv " + qa_dir_crosscal_backup_tmp +
                           " " + qa_dir_crosscal + "/")

                logger.info("Backup of crosscal plots created in {}".format(
                    qa_dir_crosscal_backup))

        # get a list all crosscal plots
        ccal_plot_list = glob.glob(
            "{0:s}/*.png".format(qa_dir_crosscal.replace("/data", "/data*")))

        if len(ccal_plot_list) == 0:
            logger.warning("No crosscal plots were found.")
        else:
            # get a unique list of plot names
            ccal_png_name_list = np.array(
                [os.path.basename(plot) for plot in ccal_plot_list])
            ccal_png_name_list = np.unique(ccal_png_name_list)

            if run_parallel:
                with pymp.Parallel(40) as p:

                    # go through all the images and merge them
                    for png_index in p.range(len(ccal_png_name_list)):

                        png_name = ccal_png_name_list[png_index]

                        # time for merging a single plot
                        start_time_plot = time()

                        logger.info("Merging {0:s}".format(png_name))

                        # get a list of plots with this name
                        ccal_plot_list = glob.glob(
                            "{0:s}/{1:s}".format(qa_dir_crosscal.replace("/data", "/data*"), png_name))

                        # now merge the images
                        try:
                            merge_plots(ccal_plot_list)
                        except Exception as e:
                            logger.warning(
                                "Merging plots for {0} failed".format(png_name))
                            logger.exception(e)
                        else:
                            logger.info(
                                "Merged plots for {0} successfully ({1:.0f}s)".format(png_name, time() - start_time_plot))
            else:
                # go through all the images and merge them
                for png_name in ccal_png_name_list:

                    # time for merging a single plot
                    start_time_plot = time()

                    logger.info("Merging {0:s}".format(png_name))

                    # get a list of plots with this name
                    ccal_plot_list = glob.glob(
                        "{0:s}/{1:s}".format(qa_dir_crosscal.replace("/data", "/data*"), png_name))

                    # now merge the images
                    try:
                        merge_plots(ccal_plot_list)
                    except Exception as e:
                        logger.warning(
                            "Merging plots for {0} failed".format(png_name))
                        logger.exception(e)
                    else:
                        logger.info(
                            "Merged plots for {0} successfully ({1:.0f}s)".format(png_name, time() - start_time_plot))

    # Merge the selfcal plots
    # ========================
    if do_scal:
        qa_dir_selfcal = os.path.join(qa_dir, "selfcal")

        logger.info("## Merging selfcal plots in {}".format(qa_dir_selfcal))

        # create a backup of the original files
        if do_backup:
            # final path of backup
            qa_dir_selfcal_backup = os.path.join(
                qa_dir_selfcal, "selfcal_gain_plots_backup")

            if os.path.exists(qa_dir_selfcal_backup):
                logger.info("Backup of selfcal gain plots already exists")
            else:
                os.mkdir(qa_dir_selfcal_backup)

                # copy the original directory
                lib.basher("mv " + os.path.join(qa_dir_selfcal, "*.png") +
                           " " + qa_dir_selfcal_backup + "/")

                logger.info("Backup of selfcal plots created in {}".format(
                    qa_dir_selfcal_backup))

        # get a list all selfcal plots
        scal_plot_list = glob.glob(
            "{0:s}/*.png".format(qa_dir_selfcal.replace("/data", "/data*")))

        if len(scal_plot_list) == 0:
            logger.warning("No selfcal plots were found.")
        else:
            # get a unique list of plot names
            scal_png_name_list = np.array(
                [os.path.basename(plot) for plot in scal_plot_list])
            scal_png_name_list = np.unique(scal_png_name_list)

            if run_parallel:

                with pymp.Parallel(40) as p:

                    # go through all the images and merge them
                    for png_index in p.range(len(scal_png_name_list)):
                        # time for merging a single plot
                        start_time_plot = time()

                        logger.info("Merging {0:s}".format(png_name))

                        # get a list of plots with this name
                        scal_plot_list = glob.glob(
                            "{0:s}/{1:s}".format(qa_dir_selfcal.replace("/data", "/data*"), png_name))

                        # now merge the images
                        try:
                            merge_plots(scal_plot_list)
                        except Exception as e:
                            logger.warning(
                                "Merging plots for {0} failed".format(png_name))
                            logger.exception(e)
                        else:
                            logger.info(
                                "Merged plots for {0} successfully ({1:.0f}s)".format(png_name, time() - start_time_plot))
            else:
                # go through all the images and merge them
                for png_name in scal_png_name_list:

                    # time for merging a single plot
                    start_time_plot = time()

                    logger.info("Merging {0:s}".format(png_name))

                    # get a list of plots with this name
                    scal_plot_list = glob.glob(
                        "{0:s}/{1:s}".format(qa_dir_selfcal.replace("/data", "/data*"), png_name))

                    # now merge the images
                    try:
                        merge_plots(scal_plot_list)
                    except Exception as e:
                        logger.warning(
                            "Merging plots for {0} failed".format(png_name))
                        logger.exception(e)
                    else:
                        logger.info(
                            "Merged plots for {0} successfully ({1:.0f}s)".format(png_name, time() - start_time_plot))

    logger.info("## Merging ... Done ({0:.0f}s)".format(time() - start_time))

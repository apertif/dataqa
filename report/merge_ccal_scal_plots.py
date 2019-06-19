from scandata import get_default_imagepath
import argparse
import time
import logging
import os
import glob
import socket
import numpy as np
from PIL import Image
from apercal.libs import lib
from time import time

def merge_plots(image_list, new_image_name=None):
    """This function does the actual merging
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


def run_merge_plots(qa_dir, do_ccal=True, do_scal=True):
    """ This function merges the crosscal and/or selfcal plots
    that are split by beam from the different data directories.
    """

    # Basic settings
    # ==============

    # get the host name
    host_name = socket.gethostname()

    # it does not make sense to run this script from another happili node
    if host_name != "happili-01":
        logger.error(
            "You are not on happili-01. This script will not work here. Abort")
        return -1

    # set whether both crosscal and selfcal plot shave to be merged or only one
    if not do_ccal and not do_scal:
        do_ccal = True
        do_scal = True

    # Merge the crosscal plots
    # ========================
    if do_ccal:
        logger.info("## Merging crosscal plots")

        qa_dir_crosscal = "{0:s}crosscal".format(qa_dir)

        # get a list all crosscal plots
        ccal_plot_list = glob.glob(
            "{0:s}/*.png".format(qa_dir_crosscal.replace("/data", "/data*")))

        if len(ccal_plot_list) == 0:
            logger.warning("No crosscal plots were found.")
        else:
            # get a unique list of plot names
            ccal_png_name_list = np.array(
                os.path.basename(plot) for plot in ccal_plot_list)
            ccal_png_name_list = np.unique(ccal_png_name_list)

            # go through all the images and merge them
            for png_name in ccal_png_name_list:

                logging.info("Merging {0:s}".format(png_name))

                # get a list of plots with this name
                ccal_plot_list = glob.glob(
                    "{0:s}/{1:s}".format(qa_dir.replace("/data", "/data*"), png_name))

                # now merge the images
                try:
                    merge_plots(ccal_plot_list)
                except Exception as e:
                    logger.warning(
                        "Merging plots for {0} failed".format(png_name))
                    logger.exception(e)
                else:
                    logger.info(
                        "Merged plots for {0} successfully".format(png_name))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate crosscal QA plots')

    # 1st argument: File name
    parser.add_argument("scan", help='Scan of target field')

    parser.add_argument("--do_ccal", action="store_true", default=False,
                        help='Set to enable merging of only the crooscal plots')

    parser.add_argument("--do_scal", action="store_true", default=False,
                        help='Set to enable merging of only the crooscal plots')

    args = parser.parse_args()

    # get the QA directory
    qa_dir = get_default_imagepath(args.scan)

    # start logging
    # Create logging file

    lib.setup_logger(
        'debug', logfile='{0:s}merge_plots.log'.format(qa_dir))
    logger = logging.getLogger(__name__)

    start_time = time.time()

    logger.info("#### Merging plots ...")

    return_msg = run_merge_plots(qa_dir, args.do_ccal, args.do_scal)

    if return_msg != 0:
        logger.warning("#### Merging plots ... Failed ({0:s}s)".format(
            time.time()-start_time))
    else:
        logger.info("#### Merging plots ... Done ({0:s}s)".format(
            time.time()-start_time))

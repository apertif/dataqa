"""
This script contains functionality to plot the selfcal images
"""

import os
from apercal.libs import lib
import glob
import socket
import logging
from astropy.io import fits
from astropy.wcs import WCS
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mc

logger = logging.getLogger(__name__)


def plot_selfcal_maps(fits_name, qa_selfcal_beam_dir):
    """This function plots the selfcal maps
    """

    fits_hdulist = fits.open(fits_name)

    # get WCS header of cube
    wcs = WCS(fits_hdulist[0].header)

    # remove unnecessary axis
    if wcs.naxis == 4:
        wcs = wcs.dropaxis(3)
        wcs = wcs.dropaxis(2)
        img = fits_hdulist[0].data[0][0]
    elif wcs.naxis == 3:
        wcs = wcs.dropaxis(2)
        img = fits_hdulist[0].data[0]
    else:
        img = fits_hdulist[0].data

    # set up plot
    ax = plt.subplot(projection=wcs)

    # create image
    fig = ax.imshow(img * 1.e3, norm=mc.SymLogNorm(0.2),  origin='lower')

    cbar = plt.colorbar(fig)
    cbar.set_label('Flux Density [mJy/beam]')

    ax.coords[0].set_axislabel('Right Ascension')
    ax.coords[1].set_axislabel('Declination')
    ax.coords[0].set_major_formatter('hh:mm')

    ax.set_title("Selfcal {0:s}".format(fits_name))

    output = "{0:s}/{1:s}".format(qa_selfcal_beam_dir,
                                  fits_name).replace(".fits", ".png")

    plt.savefig(output, overwrite=True, bbox_inches='tight', dpi=200)

    # if plot_format == "pdf":
    #     plt.savefig(output.replace(".png", ".pdf"),
    #                 overwrite=True, bbox_inches='tight')
    # else:
    #     plt.savefig(output, overwrite=True, bbox_inches='tight', dpi=300)

    plt.close("all")


def convert_mir2fits(mir_name, fits_name):
    """This function converts a miriad image to fits
    """

    fits = lib.miriad('fits')
    fits.in_ = mir_name
    fits.out = fits_name
    fits.op = 'xyout'
    try:
        fits.go()
    except Exception as e:
        logger.error(e)


def create_selfcal_maps(mir_image_list, qa_selfcal_beam_dir):
    """
    This function creates plots for the selfcal maps.
    """

    # go through the list of images
    for mir_image in mir_image_list:

        # create link to the miriad image
        link_name = os.path.basename(mir_image)
        if not os.path.exists(link_name):
            os.symlink(mir_image, link_name)
        else:
            os.unlink(link_name)
            os.symlink(mir_image, link_name)

        # get the major cycle
        major_cycle = mir_image.split("/")[-2]
        minor_cycle = os.path.basename(mir_image).split("_")[-1]

        fits_name = "{0:s}_{1:s}_{2:s}.fits".format(
            major_cycle, minor_cycle, link_name.split("_")[0])

        try:
            convert_mir2fits(link_name, fits_name)
        except Exception as e:
            logger.error(e)
            logger.error("Converting {0:s} failed".format(mir_image))

        # plot image if it exists
        if os.path.exists(fits_name):

            logger.info("Plotting {0:s}".format(mir_image))

            plot_selfcal_maps(fits_name, qa_selfcal_beam_dir)

            # remove the fits file
            try:
                os.remove(fits_name)
            except Exception as e:
                logger.error(e)
                logger.error("Could not remove {0:s}".format(fits_name))


def get_selfcal_maps(obs_id, qa_selfcal_dir):
    """
    This function goes through the images available and plots them.

    It will convert the miriad images temporarily into fits. The fits files
    will be delelted afterwards.
    At the moment only the image and residual is taken into account.
    """

    # creating a temporary directory for conversion
    tmp_convert_dir = "{0:s}tmp_conv/".format(qa_selfcal_dir)

    if not os.path.exists(tmp_convert_dir):
        os.mkdir(tmp_convert_dir)

    # get current working directory to go back to at the end of this function
    cwd = os.getcwd()

    # change to this directory for shorter path lengths for miriad
    os.chdir(tmp_convert_dir)

    # check host name
    host_name = socket.gethostname()

    if host_name != "happili-01":
        logger.warning("You are not working on happili-01.")
        logger.warning("The script will not process all beams")
        logger.warning("Please switch to happili-01")

    # get a list of data beam directories
    data_beam_dir_list = glob.glob(
        "/data*/apertif/{}/[0-3][0-9]".format(obs_id))

    if len(data_beam_dir_list) != 0:

        data_beam_dir_list.sort()

        # go through the beam directories found
        for data_beam_dir in data_beam_dir_list:

            logger.info("## Going through {0:s}".format(data_beam_dir))

            beam = data_beam_dir.split("/")[-1]

            # create beam directory in selfcal QA dir
            qa_selfcal_beam_dir = "{0:s}{1:s}".format(qa_selfcal_dir, beam)

            if not os.path.exists(qa_selfcal_beam_dir):
                os.mkdir(qa_selfcal_beam_dir)

            # get major cycles
            major_cycle_dir_list = glob.glob(
                "{0:s}/selfcal/[0-9][0-9]".format(data_beam_dir))

            if len(major_cycle_dir_list) != 0:

                # go through the major cycle directories:
                for major_cycle_dir in major_cycle_dir_list:

                    # get all images for this major cycle:
                    mir_image_list = glob.glob(
                        "{0:s}/image*".format(major_cycle_dir))

                    if len(mir_image_list) != 0:

                        # create plots for miriad selfcal images
                        create_selfcal_maps(
                            mir_image_list, qa_selfcal_beam_dir)

                    else:
                        logger.warning(
                            "No images found in {0:s}".format(major_cycle_dir))

                    # get all residuals for this major cycle:
                    mir_image_list = glob.glob(
                        "{0:s}/residual*".format(major_cycle_dir))

                    if len(mir_image_list) != 0:

                        # create plots for miriad selfcal residuals
                        create_selfcal_maps(
                            mir_image_list, qa_selfcal_beam_dir)

                    else:
                        logger.warning(
                            "No residual found in {0:s}".format(major_cycle_dir))

            else:
                logger.warning(
                    "No major selfcal cycles found for {0:s}/selfcal/".format(data_beam_dir))

    else:
        logger.error("Could not find any beams for selfcal QA")

    # switch back to working directory
    os.chdir(cwd)

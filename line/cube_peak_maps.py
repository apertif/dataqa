"""
This file contains functionality to create moment -2 maps from cubes.
Moment -2 maps take the peak of the absolute value of a spectrum from a pixel.
"""

from astropy.io import fits
from astropy.wcs import WCS
from astropy.table import Table
import numpy as np
import os
import glob
import socket
import time
import logging
from dataqa.scandata import get_default_imagepath

import matplotlib.pyplot as plt
#from scipy.optimize import curve_fit

logger = logging.getLogger(__name__)


# def gauss(x, *p):
#    """Function to calculate a Gaussian value
#    """
#    A, mu, sigma = p
#    return A*np.exp(-(x-mu)**2/(2.*sigma**2))

def plot_peak_map(fits_file, output_plot_name):
    """
    Function to plot the peak map
    """

    try:
        fits_hdulist = fits.open(cube_file)
    except Exception as e:
        logging.error(e)
        continue

    # get wcs object
    wcs = WCS(fits_hdulist[0].header)

    ax = plt.subplot(projection=wcs)

    fig = ax.imshow(
        peak_img/1.e3, vmax=np.percentile(peak_img, 0.95), origin='lower')

    cbar = plt.colorbar(fig)
    cbar.set_label('Flux Density [mJy/beam]')

    ax.coords[0].set_axislabel('Right Ascension')
    ax.coords[1].set_axislabel('Declination')
    ax.coords[0].set_major_formatter('hh:mm')

    ax.set_title("Beam {0}, Cube {1}: Moment -2".format(
        beam, os.path.basename(cube_file).split(".")[0].split("cube")[-1]))

    if plot_format == "pdf":
        plt.savefig(output.replace(".png", ".pdf"),
                    overwrite=True, bbox_inches='tight')
    else:
        plt.savefig(output, overwrite=True,
                    bbox_inches='tight', dpi=300)

        logger.debug(
            "Saving moment -2 map to {}".format(output_fits_file_name))

    plt.close("all")

    fits_hdulist.close()


def create_peak_map(cube_file, output_fits_file_name):
    """
    Function to create the peak map and save it as a fits file
    """

    # open fits file or at least try
    fits_hdulist = fits.open(cube_file)

    # get wcs object
    wcs = WCS(fits_hdulist[0].header)

    # getting rid of stokes axis and check that it is a cube
    if wcs.naxis == 4:
        wcs = wcs.dropaxis(3)
        cube = fits_hdulist[0].data[0]
    elif wcs.naxis == 3:
        cube = fits_hdulist[0].data
    else:
        logging.warning(
            "Fits file {0:s} is not a cube".format(cube_file))
        continue

    # get the shape of the cube
    cube_shape = np.shape(cube)

    # get the number of channels
    n_channels = cube_shape[0]

    # get the shape of the image
    image_shape = [cube_shape[2], cube_shape[0]]

    # create an empty image
    peak_img = np.zeros(image_shape)

    # go through each pixel and get the peak of the spectrum
    for x_pixel in range(image_shape[1]):
        for y_pixel in range(image_shape[0]):
            pixel_spec = cube[:, y_pixel, x_pixel]
            peak_img[y_pixel, x_pixel] = np.max(
                np.abs(pixel_spec))

    # creating fits image for moment -2 map
    # peak_img_hdu = fits.PrimaryHDU(img)
    # peak_img_hdu.header.update(wcs.to_header())
    # new_hdu_list = fits.HDUList([hdu])

    logger.debug(
        "Saving moment -2 map to {}".format(output_fits_file_name))
    fits.writeto(output_fits_file_name,
                 peak_img, header=wcs.to_header())

    fits_hdulist.close()


def get_cube_peak_maps(qa_line_dir, data_base_dir_list, plot_format="png"):
    """Function to get a simple rms per channel

    Args:
    -----
        qa_line_dir : str
            Directory where the line QA output is stored
        data_base_dir_list : list
            List of data directories on happili 1 to 4
        plot_format : str
            File format of map. Default: png

    """

    # go through all four data directories
    # ++++++++++++++++++++++++++++++++++++
    for data_dir in data_base_dir_list:

        start_time_data = time.time()

        logging.info("## Going through the beams in {0:s}".format(data_dir))

        # getting a list of beams
        data_dir_beam_list = glob.glob("{0:s}/[0-3][0-9]".format(data_dir))

        # checking whether no beam was found
        if len(data_dir_beam_list) != 0:

            # sort beam list
            data_dir_beam_list.sort()

            # going through all the beams that were found
            # +++++++++++++++++++++++++++++++++++++++++++
            for data_dir_beam in data_dir_beam_list:

                start_time_beam = time.time()

                # getting the beam
                beam = os.path.basename(data_dir_beam)

                logging.info("Analyzing beam {0:s}".format(beam))

                # setting the output directory for the beam
                qa_line_beam_dir = os.path.join(qa_line_dir, beam)

                # this directory does not exist create it
                if not os.path.exists(qa_line_beam_dir):
                    logging.info(
                        "Creating directory {0:s}".format(qa_line_beam_dir))
                    os.mkdir(qa_line_beam_dir)

                # set the name of the of the cube file to analyze
                cube_file = "{0:s}/line/cubes/HI_image_cube*.fits".format(
                    data_dir_beam)

                # there are several cubes
                cube_file_list = glob.glob(cube_file.replace("cube", "cube*"))

                # continue only if glob has found cubes
                if len(cube_file_list) != 0:

                    cube_file_list.sort()

                    for cube_file in cube_file_list:

                        # make sure the cube file exists:
                        if os.path.exists(cube_file):

                            logger.info(
                                "Getting moment -2 map for cube {}".format(cube_file))

                            # Create peak map
                            output_fits_file_name = os.path.join(qa_line_beam_dir, os.path.basename(cube_file).replace(
                                ".fits", "_moment_-2.fits"))
                            try:
                                create_peak_map(
                                    cube_file, output_fits_file_name)
                            except Exception as e:
                                logging.error(e)
                                continue

                            # Create plot
                            output_plot_name = output_fits_file_name.replace(
                                ".fits", ".png")
                            try:
                                plot_peak_map(
                                    output_fits_file_name, output_plot_name)
                            except Exception as e:
                                logging.error(e)
                                continue
                        else:
                            logger.warning(
                                "Could not find file {}".format(cube_file))

                    logging.info(
                        "Finished analyzing cube {0}".format(cube_file))
                else:
                    logging.warning(
                        "No HI cubes found for beam {0:s}".format(beam))

            logging.info("Finished analyzing beam {0:s} ({1:.1f}s)".format(
                beam, time.time()-start_time_beam))
        else:
            logging.warning("No beams found in {0:s}".format(data_dir))

    logging.info("Finished going through data directory {0:s} ({1:.1f}s)".format(
        data_dir, time.time()-start_time_data))

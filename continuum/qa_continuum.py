"""
This script contains function to run pybdsf for the continuum QA.
"""

import numpy as np
import logging
import bdsf
import os
import time
import logging
import socket
from apercal.libs import lib
import sys
import glob
from astropy.io import fits
from astropy.wcs import WCS
from astropy.table import Table
import matplotlib.pyplot as plt
import scipy
from dataqa.continuum.validation_tool import validation

logger = logging.getLogger(__name__)


def get_image_from_fits(fits_file):
    """Function to get the image from a fits file

    Parameter:
        fits_file : str
            File name of the image fits file

    Return:
        img : array
            The image from the fits file of an array
    """

    its_file = fits.open(fits_file)

    # check the number image axis
    wcs = WCS(fits_hdulist[0].header)
    if wcs.naxis == 4:
        img = fits_hdulist[0].data[0][0]
    elif wcs.naxis == 3:
        img = fits_hdulist[0].data[0]
    else:
        img = fits_hdulist[0].data

    # close the fits file
    fits_file.close()

    return img


def qa_check_image_gaussianity(fits_file, alpha=1.e-2):
    """Check if an image has gaussian distribution

    Note:
        Function was taken from apercal.subs.qa.checkimagegaussianity

    Parameter:
        fits_file : str
            The name of the fits image to process
        alpha : float (default 1e-2)
            Parameter to judge the gaussianity, default taken from apercal conifg

    Returns:
        True if image is ok, False otherwise
    """

    img = get_image_from_fits(fits_file)

    # determin gaussianity
    k2, p = scipy.stats.normaltest(img, nan_policy='omit', axis=None)
    if p < alpha:
        return True
    else:
        return False


def qa_get_image_dr(fits_file, rms):
    """Function to determine the image dynamic range

    Note:
        fits_file : str
            The name of the fits image to process
        rms : float
            The noise level of the image

    Returns:
        image_dr : float
            The image dynamic range
    """

    img = get_image_from_fits(fits_file)

    image_dr = np.max(img) / rms

    return image_dr


def qa_get_source_cat_dr(fits_file, rms, qa_pybdsf_dir):
    """Function to determine the dynamic range in the source catalog

    Note:
        fits_file : str
            The name of the fits image to process
        rms : float
            The noise level of the image
        qa_pybdsf_dir : str
            The path to the directory where the QA (and pybdsft output) is stored

    Returns:
        source_cat_dr : float
            The dynamic range in the source catalogue
    """

    # get name of source catalogue
    source_cat_name = "{0:s}/{1:s}".format(qa_pybdsf_dir, os.path.basename(
        fits_file).replace(".fits", "_pybdsf_cat.csv"))

    # read pybdsf catalog
    cat_data = Table.read(source_cat_name, format=source_cat_name.split(
        ".")[-1], header_start=4, data_start=5)

    # search for dynamic range in catalogue

    return 0


def qa_get_image_noise_dr_gaussianity(fits_file, qa_pybdsf_dir):
    """This functions determines additional image QA informaiton.

    Note:
        The function determines the image noise, the local dynamic range and gaussianity of an image

    Parameter:
        fits_file : str
            The file name of the fits image to process
        qa_pybdsf_dir : str
            The directory of the continuum or mosaic QA where the output should be saved to

    """

    logger.info("# Performing additional QA tests...")

    # Checking noise noise
    # +++++++++++++++++++

    # get the residual continuum image
    rms = 1

    # Checking image dynamic range
    # ++++++++++++++++++++++++++++
    logger.info("Determining image dynamic range ...")
    image_dyanmic_range = qa_get_image_dr(fits_file, rms)
    logger.info("Image dynamic range is: {0:.3g}".format(image_dyanmic_range))

    # Checking source dynamic range
    # +++++++++++++++++++++++++++++
    logger.info("Determining source catalogue dynamic range ...")
    source_cat_dyanmic_range = qa_get_source_cat_dr(
        fits_file, rms, qa_pybdsf_dir)
    logger.info("Source catalogue dynamic range is: {0:.3g}".format(
        source_cat_dyanmic_range))

    # Checking local dynamic range
    # ++++++++++++++++++++++++++++

    # Checkking gaussianity
    # +++++++++++++++++++++

    logger.info("Testing Gaussianity ...")

    gaussianity_confirm = qa_check_image_gaussianity(fits_file)

    logger.info("Image fullfills gaussianity: {0}".format(gaussianity_confirm))

    # Write output file as xml
    # ++++++++++++++++++++++++
    output_file_name = "{0:s}/{1:s}".format(
        qa_pybdsf_dir, os.path.basename(fits_file).replace(".fits", "QA_info.xml"))


def qa_plot_pybdsf_images(fits_file_list, plot_name_list, plot_format="png"):
    """This function creates quick plots of the diagnostic fits files

    Note:
        By default the images are created in png format with 400dpi, but it
        is possible to choose pdf

    Parameter:
        fits_file_list : list
            A list of strings with the file names of the fits files
        plot_name : list
            A list of strings with the names of the plots to save
        plot_format : str (default png)
            The format of the plot for matplotlib

    """

    # number of files
    n_fits_files = len(fits_file_list)

    logger("Plotting PyBDSF diagnostic plots")

    # go through the types of images and plot them
    for k in range(n_fits_files):

        fits_hdulist = fits.open(fits_file_list[k])

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
        fig = ax.imshow(img * 1.e3, origin='lower')

        cbar = plt.colorbar(fig)
        cbar.set_label('Flux Density [mJy/beam]')

        ax.coords[0].set_axislabel('Right Ascension')
        ax.coords[1].set_axislabel('Declination')
        ax.coords[0].set_major_formatter('hh:mm')
        ax.set_title("{0:s}".format(os.path.basename(fits_file_list[k])))

        output = plot_name_list[k]

        if plot_format == "pdf":
            plt.savefig(output.replace(".png", ".pdf"),
                        overwrite=True, bbox_inches='tight')
        else:
            plt.savefig(output, overwrite=True, bbox_inches='tight', dpi=400)

        plt.close("all")

    logger("Plotting PyBDSF diagnostic plots. Done")


def qa_continuum_run_pybdsf_validation(data_basedir_list, qa_pybdsf_dir, overwrite=True):
    """This function runs pybdsf on the continuum image of each beam

    This function will create a new directory for each beam. In this sub-directory
    the fits image and the pybdsf output will be saved.
    In the end the function will provide information on how many directories, beams,
    or pybdsf runs failed.

    Note:
        The function will always overwrite existing files.

    Parameter:
        data_basedir_list : list
            List of data directories on the happili node

        qa_pybdsf_dir : str
            The directory of the QA where the output will be saved.
            Most likely this is /home/<user>/qa_science_demo_2019/continuum/

    Return:
        run_pybdsf_status : int
            Status of how well this function performed

    """

    logger.info("#### Running pybdsf for each beam")

    # number of directories to go through
    n_data_basedir = len(data_basedir_list)

    # counter for failed number of directories, images found, and pybdsf runs
    n_data_dir_failed = 0
    n_pybdsf_failed = 0
    n_images_failed = 0

    # counter for number of beams
    n_beams_total = 0

    # Go through all the different data directories
    for data_basedir in data_basedir_list:

        # get the beams in this directory
        beam_data_dir_list = glob.glob("{0:s}/[0-3][0-9]".format(data_basedir))
        beam_data_dir_list.sort()

        # number of beams
        n_beams = len(beam_data_dir_list)

        n_beams_total += n_beams

        # check that beams exists
        if n_beams == 0:
            logger.error("No beams found. Abort")
            n_data_dir_failed += 1
            continue
        else:
            logger.info("Found {0:d} beams".format(n_beams))

        # get a list of only the beams
        beam_list = [os.path.basename(beam) for beam in beam_data_dir_list]

        # Now go through each beam
        for k in range(n_beams):

            beam = beam_list[k]
            beam_data_dir = beam_data_dir_list[k]

            logger.info("## Processing beam {0:02d}".format(int(beam)))

            beam_pybdsf_dir = "{0:s}/{1:s}".format(qa_pybdsf_dir, beam)

            # check/create beam directory
            if not os.path.exists(beam_pybdsf_dir):
                logger.info(
                    "Creating directory {0:s}".format(beam_pybdsf_dir))

            # # change to this directory
            # os.chdir(beam_pybdsf_dir)

            # directory of continuum images
            continuum_image_dir = "{0:s}/continuum".format(beam_data_dir)

            # Get the fits image
            fits_image = glob.glob("{0:s}/*.fits".format(continuum_image_dir))

            if len(fits_image) == 0:
                logger.error(
                    "Did not find any fits image for beam {0:s}".format(beam))
                continue
            elif len(fits_image) == 1:
                fits_image = fits_image[0]
            else:
                fits_image.sort()
                logger.warning(
                    "Found more than one fits image for beam {0:s}. Take the last one".format(beam))
                fits_image = fits_image[-1]

            # run pybdsf
            logger.info("# Running validation tool and pybdsf")
            try:

                # change into the directory where the QA products should be produced
                # This is necessary for the current implementation of the validation tool
                # Should it return to the initial directory?
                os.chdir(qa_pybdsf_dir)

                # run validation tool and pybdsf combined
                validation.run(fits_image)

                # img = bdsf.process_image(fits_image, quiet=True)

                # # Check/create catalogue name
                # cat_file = "{0:s}/{1:s}".format(beam_pybdsf_dir, os.path.basename(
                #     fits_image).replace(".fits", "_pybdsf_cat.fits"))

                # # Write catalogue as csv file
                # logger.info("# Writing catalogue")
                # img.write_catalog(outfile=cat_file,
                #                   format='fits', clobber=True)

                # # Save plots
                # logger.info("# Saving pybdsf plots")
                # plot_type_list = ['rms', 'mean',
                #                   'gaus_model', 'gaus_resid', 'island_mask']
                # fits_names = [cat_file.replace(
                #     ".fits", "_{0:s}.fits".format(plot)) for plot in plot_type_list]
                # plot_names = [fits.replace(
                #     ".fits", ".png") for fits in fits_names]

                # # number of plots
                # n_plots = len(plot_type_list)

                # for k in range(n_plots):
                #     img.export_image(outfile=fits_names[k],
                #                      clobber=overwrite, img_type=plot_type_list[k])

                logger.info("# Running validation tool and pybdsf. Done")
            except Exception as e:
                logger.error(e)
                logger.error("# Running validation tool and pybdsf failed.")
                n_pybdsf_failed += 1

            plot_type_list = ['rms', 'mean',
                              'gaus_model', 'gaus_resid', 'island_mask']
            fits_names = [os.path.basename(fits_image).replace(
                ".fits", "pybdsf_{0:s}.fits".format(plot)) for plot in plot_type_list]

            plot_names = [fits.replace(
                ".fits", ".png") for fits in fits_names]

            # add the continuum image
            fits_names.append(fits_image)
            plot_names.append(os.path.basename(
                fits_image).replace(".fits", ".png"))

            # create images without a lot of adjusting
            try:
                qa_plot_pybdsf_images(fits_names, plot_names)
            except Exception as e:
                logger.error(e)
                logger.error("Plotting PyBDSF diagnostic images failed")

    # assuming everything went fine
    run_pybdsf_validation_status = 1

    # Check how many data directories failed as a whole
    if n_data_dir_failed == n_data_basedir:
        logger.error("No beams found in all data directories")
        run_pybdsf_validation_status = -1
    elif n_data_dir_failed < n_data_basedir:
        logger.warning("Could not find any beams in {0:d} data directories (out of {1:d}). Check log file".format(
            n_data_dir_failed, n_data_basedir))
        run_pybdsf_validation_status = 2

    # Check how many beams failed
    if n_images_failed == n_beams_total:
        logger.error(
            "Did not find any continuum images to convert or conversion failed")
        run_pybdsf_validation_status = -1
    elif n_images_failed < n_beams_total:
        logger.warning("Could not find or convert {0:d} continuum images (out of {1:d}). Check log file".format(
            n_images_failed, n_beams_total))
        run_pybdsf_validation_status = 2

    # Check how often pybdsf failed
    if n_pybdsf_failed == n_beams_total:
        logger.error(
            "PyBDSF and validation tool failed on all images")
        run_pybdsf_validation_status = -1
    elif n_pybdsf_failed < n_beams_total:
        logger.warning("PyBDSF and validation tool failed on {0:d} continuum images (out of {1:d}). Check log file".format(
            n_pybdsf_failed, n_beams_total))
        run_pybdsf_validation_status = 2

    return run_pybdsf_validation_status

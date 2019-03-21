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


def qa_get_source_cat_dr(fits_file, rms, qa_validation_dir):
    """Function to determine the dynamic range in the source catalog

    Note:
        fits_file : str
            The name of the fits image to process
        rms : float
            The noise level of the image
        qa_validation_dir : str
            The path to the directory where the QA (and pybdsft output) is stored

    Returns:
        source_cat_dr : float
            The dynamic range in the source catalogue
    """

    # get name of source catalogue
    source_cat_name = "{0:s}/{1:s}".format(qa_validation_dir, os.path.basename(
        fits_file).replace(".fits", "_pybdsf_cat.csv"))

    # read pybdsf catalog
    cat_data = Table.read(source_cat_name, format=source_cat_name.split(
        ".")[-1], header_start=4, data_start=5)

    # search for dynamic range in catalogue

    return 0


def qa_get_image_noise_dr_gaussianity(fits_file, qa_validation_dir):
    """This functions determines additional image QA informaiton.

    Note:
        The function determines the image noise, the local dynamic range and gaussianity of an image

    Parameter:
        fits_file : str
            The file name of the fits image to process
        qa_validation_dir : str
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
        fits_file, rms, qa_validation_dir)
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
        qa_validation_dir, os.path.basename(fits_file).replace(".fits", "QA_info.xml"))


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


def get_continuum_fits_images(data_basedir_list, qa_validation_dir, save_table=True):
    """Function that gets the list of existing continuum fits images for each beam.

    Note:
        The function goes through the four data directories and collects all fits image
        it finds for the beams. It accounts for missing fits images

    Parameter:
        data_basedir_list : list
            The data directories on happili
        qa_validation_dir : str
            Directory where the QA is stored
        save_table : bool (default True)
            Save the list of fits files to the QA directory

    Return:
        fits_file_table : Astropy Table
            The beams and path to the continuum image
    """

    # this is how many beams there should be
    n_beams_total = 40

    # create table with columns of a beam id, the actual beam name, and the fits image path
    beam_id = np.arange(n_beams_total)
    beams = ['{0:02d}'.format(beam) for beam in range(n_beams_total)]
    beam_exists = [False for beam in range(n_beams_total)]
    fits_image_exists = [False for beam in range(n_beams_total)]
    fits_file_path = ['' for beam in range(n_beams_total)]

    fits_file_table = Table([beam_id, beams, fits_file_path, beam_exists, fits_image_exists], names=(
        'beam_id', 'beam_name', 'fits_image_path', 'beam_exists', 'fits_image_exists'))

    # count how many beams and fits files were found
    n_beams_found_total = 0
    n_fits_images_found = 0

    logger.info("Getting a list of continuum fits images")

    # Go through all the different data directories
    for data_basedir in data_basedir_list:

        # get the beams in this directory
        beam_data_dir_list = glob.glob("{0:s}/[0-3][0-9]".format(data_basedir))
        beam_data_dir_list.sort()

        # number of beams
        n_beams = len(beam_data_dir_list)

        # total number of beams found
        n_beams_found_total += n_beams

        # check that beams exists
        if n_beams == 0:
            logger.error(
                "No beams found in {0:s}. Go to next data directory".format(data_basedir))
            continue
        else:
            logger.info("Found {0:d} beams in {1:s}".format(
                n_beams, data_basedir))

        # Now go through each beam
        for beam_dir in beam_data_dir_list:

            # get a list of only the beams
            beam = os.path.basename(beam_dir)

            # directory of continuum images
            continuum_image_dir = "{0:s}/continuum".format(beam_dir)

            # Get the fits image
            fits_image = glob.glob("{0:s}/*.fits".format(continuum_image_dir))

            # check whether no fits file was found, one or more fits file
            # the latter case should not exists, but I do not want it to stop
            if len(fits_image) == 0:
                logger.error(
                    "Did not find any fits image for beam {0:s}".format(beam))
                continue
            elif len(fits_image) == 1:
                fits_image = fits_image[0]
                n_fits_images_found += 1
            else:
                fits_image.sort()
                logger.warning(
                    "Found more than one fits image for beam {0:s}. Take the last one".format(beam))
                fits_image = fits_image[-1]
                n_fits_images_found += 1

            # get the index for the table where path should be stored
            table_beam_index = np.where(
                fits_file_table['beam_name'] == beam)[0]

            # there should always be a match, but just in case
            try:
                fits_file_table['fits_image_path'][table_beam_index] = fits_image
                fits_file_table['beam_exists'][table_beam_index] = True
                fits_file_table['fits_image_exists'][table_beam_index] = True
            except Exception as e:
                logger.error(e)
                logger.error(
                    "Could not match beam {0:s} to table of fits images".format(beam))

    # Check how many beams failed
    if n_beams_found_total < n_beams_total:
        logger.warning("Found {0:d} out of {1:d} beams".format(
            n_beams_found_total, n_beams_total))
    else:
        logger.info("Found all {0:d} images".format(n_beams_found_total))

    # check how many fits files were found
    if n_fits_images_found < n_beams_found_total:
        logger.warning(
            "Found {0:d} fits images out of {1:d} available beams".format(n_fits_images_found, n_beams_found_total))
    else:
        logger.info("Found a fits file for each of the {0:d}".format(
            n_beams_found_total))

    # save the file
    if save_table:
        save_name = "{0:s}/fits_image_list.csv".format(qa_validation_dir)
        logger.info("Saving table with fits images to {0:s}".format(save_name))
        fits_file_table.write(save_name, format="csv")

    # return the table
    return fits_file_table


def qa_continuum_run_validation(data_basedir_list, qa_validation_dir, overwrite=True):
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

        qa_validation_dir : str
            The directory of the QA where the output will be saved.
            Most likely this is /home/<user>/qa_science_demo_2019/continuum/

    Return:
        run_pybdsf_status : int
            Status of how well this function performed

    """

    logger.info("#### Running validation for each beam")

    # get the available fits images for the available beams
    fits_file_table = get_continuum_fits_images(
        data_basedir_list, qa_validation_dir)

    for beam_index in fits_file_table['beam_id']:

        # create a subdirectory for the beam in the qa directory
        qa_validation_beam_dir = "{0:s}/{1:s}".format(
            qa_validation_dir, fits_file_table['beam_name'])

        if not os.path.exists(qa_validation_beam_dir):
            logger.info("Creating {0:s}".format(qa_validation_beam_dir))

        fits_image = fits_file_table['fits_image_path'][beam_index]

        if fits_image == '':
            logger.warning("No fits image for beam {0:d}".format(
                fits_file_table['beam_name'][beam_index]))
        else:
            # run pybdsf
            logger.info("## Running validation tool and pybdsf")
            try:

                # change into the directory where the QA products should be produced
                # This is necessary for the current implementation of the validation tool
                # Should it return to the initial directory?
                os.chdir(qa_validation_dir)

                # run validation tool and pybdsf combined
                validation.run(fits_image)

                logger.info("## Running validation tool. Done")
            except Exception as e:
                logger.error(e)
                logger.error("## Running validation tool failed.")

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
                logger.error("## Plotting PyBDSF diagnostic images failed")

    #     # Go through all the different data directories
    # for data_basedir in data_basedir_list:

    #     # get the beams in this directory
    #     beam_data_dir_list = glob.glob("{0:s}/[0-3][0-9]".format(data_basedir))
    #     beam_data_dir_list.sort()

    #     # number of beams
    #     n_beams = len(beam_data_dir_list)

    #     n_beams_total += n_beams

    #     # check that beams exists
    #     if n_beams == 0:
    #         logger.error("No beams found. Abort")
    #         n_data_dir_failed += 1
    #         continue
    #     else:
    #         logger.info("Found {0:d} beams".format(n_beams))

    #     # get a list of only the beams
    #     beam_list = [os.path.basename(beam) for beam in beam_data_dir_list]

    #     # Now go through each beam
    #     for k in range(n_beams):

    #         beam = beam_list[k]
    #         beam_data_dir = beam_data_dir_list[k]

    #         logger.info("## Processing beam {0:02d}".format(int(beam)))

    #         beam_pybdsf_dir = "{0:s}/{1:s}".format(qa_validation_dir, beam)

    #         # check/create beam directory
    #         if not os.path.exists(beam_pybdsf_dir):
    #             logger.info(
    #                 "Creating directory {0:s}".format(beam_pybdsf_dir))

    #         # # change to this directory
    #         # os.chdir(beam_pybdsf_dir)

    #         # directory of continuum images
    #         continuum_image_dir = "{0:s}/continuum".format(beam_data_dir)

    #         # Get the fits image
    #         fits_image = glob.glob("{0:s}/*.fits".format(continuum_image_dir))

    #         if len(fits_image) == 0:
    #             logger.error(
    #                 "Did not find any fits image for beam {0:s}".format(beam))
    #             continue
    #         elif len(fits_image) == 1:
    #             fits_image = fits_image[0]
    #         else:
    #             fits_image.sort()
    #             logger.warning(
    #                 "Found more than one fits image for beam {0:s}. Take the last one".format(beam))
    #             fits_image = fits_image[-1]

    #         # run pybdsf
    #         logger.info("# Running validation tool and pybdsf")
    #         try:

    #             # change into the directory where the QA products should be produced
    #             # This is necessary for the current implementation of the validation tool
    #             # Should it return to the initial directory?
    #             os.chdir(qa_validation_dir)

    #             # run validation tool and pybdsf combined
    #             validation.run(fits_image)

    #             # img = bdsf.process_image(fits_image, quiet=True)

    #             # # Check/create catalogue name
    #             # cat_file = "{0:s}/{1:s}".format(beam_pybdsf_dir, os.path.basename(
    #             #     fits_image).replace(".fits", "_pybdsf_cat.fits"))

    #             # # Write catalogue as csv file
    #             # logger.info("# Writing catalogue")
    #             # img.write_catalog(outfile=cat_file,
    #             #                   format='fits', clobber=True)

    #             # # Save plots
    #             # logger.info("# Saving pybdsf plots")
    #             # plot_type_list = ['rms', 'mean',
    #             #                   'gaus_model', 'gaus_resid', 'island_mask']
    #             # fits_names = [cat_file.replace(
    #             #     ".fits", "_{0:s}.fits".format(plot)) for plot in plot_type_list]
    #             # plot_names = [fits.replace(
    #             #     ".fits", ".png") for fits in fits_names]

    #             # # number of plots
    #             # n_plots = len(plot_type_list)

    #             # for k in range(n_plots):
    #             #     img.export_image(outfile=fits_names[k],
    #             #                      clobber=overwrite, img_type=plot_type_list[k])

    #             logger.info("# Running validation tool and pybdsf. Done")
    #         except Exception as e:
    #             logger.error(e)
    #             logger.error("# Running validation tool and pybdsf failed.")
    #             n_pybdsf_failed += 1

    #         plot_type_list = ['rms', 'mean',
    #                           'gaus_model', 'gaus_resid', 'island_mask']
    #         fits_names = [os.path.basename(fits_image).replace(
    #             ".fits", "pybdsf_{0:s}.fits".format(plot)) for plot in plot_type_list]

    #         plot_names = [fits.replace(
    #             ".fits", ".png") for fits in fits_names]

    #         # add the continuum image
    #         fits_names.append(fits_image)
    #         plot_names.append(os.path.basename(
    #             fits_image).replace(".fits", ".png"))

    #         # create images without a lot of adjusting
    #         try:
    #             qa_plot_pybdsf_images(fits_names, plot_names)
    #         except Exception as e:
    #             logger.error(e)
    #             logger.error("Plotting PyBDSF diagnostic images failed")

    # # assuming everything went fine
    # run_pybdsf_validation_status = 1

    # # Check how often pybdsf failed
    # if n_pybdsf_failed == n_beams_total:
    #     logger.error(
    #         "PyBDSF and validation tool failed on all images")
    #     run_pybdsf_validation_status = -1
    # elif n_pybdsf_failed < n_beams_total:
    #     logger.warning("PyBDSF and validation tool failed on {0:d} continuum images (out of {1:d}). Check log file".format(
    #         n_pybdsf_failed, n_beams_total))
    #     run_pybdsf_validation_status = 2

    # return run_pybdsf_validation_status

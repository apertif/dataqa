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

logger = logging.getLogger(__name__)

def qa_continuum_pybdsf_convert_mir2fits(obs_id, mir_image, fits_image):
    """This function converts a miriad image to a fits image

    Paramter:
        obs_id : int
            Observation number which is processed

        mir_image : str
            Full path name of miriad image to be converted

        fits_image : str
            Name of fits image which the miriad image will be converted into

    Return:
        1 if conversion was successful
        -1 if conversion was unsuccessful
    """

    # get only the name of the image
    mir_image_name = os.path.basename(mir_image)

    # create a link to the miriad file
    os.symlink(mir_image, mir_image_name)

    logging.info("Convert {0:s} to {1:s}".format(mir_image_name, fits_image))

    fits = lib.miriad('fits')
    fits.op = 'xyout'
    fits.in_ = mir_image_name
    fits.out = fits_image
    fits.go()

    # check that the beam was actually created
    if os.path.exists(fits_image):
        return 1
    else:
        # conversion failed
        return -1


def qa_continuum_run_pybdsf(obs_id, data_basedir_list, qa_pybdsf_dir):
    """This function runs pybdsf on the continuum image of each beam

    This function will create a new directory for each beam. In this sub-directory
    the fits image and the pybdsf output will be saved.
    In the end the function will provide information on how many directories, beams,
    or pybdsf runs failed.

    Note:
        The function will always overwrite existing files.

    Parameter:
        obs_id : int
            Observation number

        data_basedir_list : list
            List of data directories on the happili node

        qa_pybdsf_dir : str
            The directory of the QA where the output will be saved.
            Most likely this is /home/<user>/qa_science_demo_2019/continuum/

    Return:
        run_pybdsf_status : int
            Status of how well this function performed

    """

    logging.info("#### Running pybdsf for each beam")

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
            logging.error("No beams found. Abort")
            n_data_dir_failed += 1
            continue
        else:
            logging.info("Found {0:d} beams".format(n_beams))

        # get a list of only the beams
        beam_list = [beam.split('/')[-1] for beam in beam_data_dir_list]

        # Now go through each beam
        for k in range(n_beams):

            beam = beam_list[k]
            beam_data_dir = beam_data_dir_list[k]

            logging.info("## Processing beam {0:02d}".format(int(beam)))

            beam_pybdsf_dir = "{0:s}/{1:s}".format(qa_pybdsf_dir, beam)

            # check/create beam directory
            if not os.path.exists(beam_pybdsf_dir):
                logging.info(
                    "Creating directory {0:s}".format(beam_pybdsf_dir))

            # change to this directory
            os.chdir(beam_pybdsf_dir)

            # directory of continuum images
            continuum_image_dir = "{0:s}/continuum".format(beam_data_dir)

            # Collect all the images that are in this directory
            mir_image_list = glob.glob(
                "{0:s}/image_mf_[0-9][0-9]".format(continuum_image_dir))

            # check that there actually is an image, if not continue with next beam
            if len(mir_image_list) == 0:
                logging.error(
                    "No image found for beam {0:s}. Continue with next beam".format(beam))
                n_images_failed += 1
                continue

            # sort the image list
            mir_image_list.sort()

            # get the image with the highest number
            # should be the last in the array after sorting
            mir_image = mir_image_list[-1]

            # name of the fits image
            fits_image = "{0:d}_beam_{1:s}_continuum_image.fits".format(
                obs_id, beam)

            # convert the image to fits
            convert_stat = qa_continuum_pybdsf_convert_mir2fits(
                obs_id, mir_image, fits_image)

            if convert_stat == 1:
                logging.info("Convert was successful")
            else:
                logging.error("Convert failed. Continue with next beam")
                n_images_failed += 1
                continue

            # run pybdsf
            logging.info("# Running pybdsf")
            try:
                img = bdsf.process_image(fits_image, quiet=True)

                # Check/create catalogue name
                cat_file = fits_image.replace(".fits", "_pybdsf_cat.csv")

                # Write catalogue as csv file
                logging.info("# Writing catalogue")
                img.write_catalog(outfile=cat_file, format='csv', clobber=True)

                # Save plots
                logging.info("# Saving pybdsf plots")
                plot_type_list = ['rms', 'mean',
                                  'gaus_model', 'gaus_resid', 'island_mask']
                for plot_type in plot_type_list:
                    plot_name = cat_file.replace(
                        ".csv", "_{0:s}.fits".format(plot_type))
                    img.export_image(outfile=plot_name, clobber=True,
                                     img_type=plot_type)
            except Exception as e:
                logger.error(e)
                n_pybdsf_failed += 1

    # assuming everything went fine
    run_pybdsf_status = 1

    # Check how many data directories failed as a whole
    if n_data_dir_failed == n_data_basedir:
        logging.error("No beams found in all data directories")
        run_pybdsf_status = -1
    elif n_data_dir_failed < n_data_basedir:
        logging.warning("Could not find any beams in {0:d} data directories (out of {1:d}). Check log file".format(
            n_data_dir_failed, n_data_basedir))
        run_pybdsf_status = 2

    # Check how many beams failed
    if n_images_failed == n_beams_total:
        logging.error(
            "Did not find any continuum images to convert or conversion failed")
        run_pybdsf_status = -1
    elif n_images_failed < n_beams_total:
        logging.warning("Could not find or convert {0:d} continuum images (out of {1:d}). Check log file".format(
            n_images_failed, n_beams_total))
        run_pybdsf_status = 2

    # Check how often pybdsf failed
    if n_pybdsf_failed == n_beams_total:
        logging.error(
            "PyBDSF failed on all images")
        run_pybdsf_status = -1
    elif n_pybdsf_failed < n_beams_total:
        logging.warning("PyBDSF failed on {0:d} continuum images (out of {1:d}). Check log file".format(
            n_pybdsf_failed, n_beams_total))
        run_pybdsf_status = 2

    return run_pybdsf_status

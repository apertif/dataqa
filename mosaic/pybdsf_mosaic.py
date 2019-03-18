import numpy as np
import logging
import bdsf
import os
import time
import logging
import socket
#from apercal.libs import lib
import sys
import glob
from astropy.io import fits
from astropy.wcs import WCS

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def qa_mosaic_plot_pybdsf_images(fits_names, plot_format="png"):
    """This function creates quick plots of the diagnostic fits files

    """

    print("Plotting PyBDSF diagnostic plots")

    # go through the types of images and plot them
    for fits_file in fits_names:

        fits_hdulist = fits.open(fits_file)

        # get WCS header of cube
        wcs = WCS(fits_hdulist[0].header)

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
        ax.set_title("{0:s}".format(os.path.basename(fits_file)))

        output = fits_file.replace("fits", plot_format)

        if plot_format == "pdf":
            plt.savefig(output.replace(".png", ".pdf"),
                        overwrite=True, bbox_inches='tight')
        else:
            plt.savefig(output, overwrite=True, bbox_inches='tight', dpi=400)

    print("Plotting PyBDSF diagnostic plots. Done")


def qa_mosaic_run_pybdsf(obs_id, mosaic_name, qa_pybdsf_dir, output_name='', overwrite=True):
    """This function runs pybdsf on a mosaic image.

    It can also be used to run pybdsf on a single image.

    Note:
        The function assumes that the mosaic image is a fits file

    Parameter:
        obs_id : int
            Observation number

        mosaic_name : str
            Name of the mosaic image fits

        qa_pybdsf_dir : str
            The directory of the QA where the output will be saved.
            Most likely this is /home/<user>/qa_science_demo_2019/mosaic/pybdsf/

        output_name : str (default '')
            Set the name of the output image

        overwrite : bool (default True)
            Set whether existing pybdsf files should be overwritten

    Return:
        run_pybdsf_status : int
            Status of how well this function performed

    """

    # change the working directory to where the qa directory
    os.chdir(qa_pybdsf_dir)

    # Create a link to the fits file so that the pybdsf log file is stored in the qa directory
    image_name = os.path.basename(mosaic_name)

    if not os.path.exists(image_name):
        os.symlink(mosaic_name, image_name)

    # try:
    #     os.symlink(mosaic_name, image_name)
    # except Exception e:
    #     return -1

    # Check/create catalogue name
    if output_name == '':
        cat_file = "{0:s}/{1:d}_mosaic_pybdsf.fits".format(
            qa_pybdsf_dir, obs_id)
    else:
        cat_file = output_name

    # assuming pybdsf will work
    run_pybdsf_status = 1

    # Run pybdsf on the input image
    logging.info("#### Running pybdsf")
    try:
        img = bdsf.process_image(image_name, quiet=True)
        # img = bdsf.process_image(image_name, quiet=True, output_opts=True, plot_allgaus=True, plot_islands=True,
        #                          savefits_meanim=True, savefits_normim=True, savefits_rankim=True, savefits_residim=True, savefits_rmsim=True)

        # Write catalogue as csv file
        logging.info("#### Writing catalogue")
        img.write_catalog(outfile=cat_file, format='fits', clobber=True)

        # Save plots
        logging.info("#### Saving pybdsf plots")
        plot_type_list = ['rms', 'mean',
                          'gaus_model', 'gaus_resid', 'island_mask']
        plot_names = [cat_file.replace(
            ".fits", "_{0:s}.fits".format(plot)) for plot in plot_type_list]
        # plot_type_list = ['gaus_model', 'gaus_resid', 'island_mask']

        # number of plots
        n_plots = len(plot_type_list)

        for k in range(n_plots):
            img.export_image(outfile=plot_names[k],
                             clobber=overwrite, img_type=plot_type_list[k])

        # create images without a lot of adjusting
        qa_mosaic_plot_pybdsf_images(plot_names)

    except Exception as e:
        logger.error(e)
        logger.error("PyBDSF failed on image {0:s}".format(image_name))
        run_pybdsf_status = -1

    return run_pybdsf_status

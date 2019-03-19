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
import matplotlib.pyplot as plt
from ..continuum.validation import validation
from ..continuum.qa_continuum import qa_plot_pybdsf_images

logger = logging.getLogger(__name__)

# def qa_mosaic_plot_pybdsf_images(fits_file_list, plot_name_list, plot_format="png"):
#     """This function creates quick plots of the diagnostic fits files

#     Note:
#         By default the images are created in png format with 400dpi, but it
#         is possible to choose pdf

#     Parameter:
#         fits_file_list : list
#             A list of strings with the file names of the fits files
#         plot_name : list
#             A list of strings with the names of the plots to save
#         plot_format : str (default png)
#             The format of the plot for matplotlib

#     """

#     # number of files
#     n_fits_files = len(fits_file_list)

#     print("Plotting PyBDSF diagnostic plots")

#     # go through the types of images and plot them
#     for k in range(n_fits_files):

#         fits_hdulist = fits.open(fits_file_list[k])

#         # get WCS header of cube
#         wcs = WCS(fits_hdulist[0].header)

#         if wcs.naxis == 4:
#             wcs = wcs.dropaxis(3)
#             wcs = wcs.dropaxis(2)
#             img = fits_hdulist[0].data[0][0]
#         elif wcs.naxis == 3:
#             wcs = wcs.dropaxis(2)
#             img = fits_hdulist[0].data[0]
#         else:
#             img = fits_hdulist[0].data

#         # set up plot
#         ax = plt.subplot(projection=wcs)

#         # create image
#         fig = ax.imshow(img * 1.e3, origin='lower')

#         cbar = plt.colorbar(fig)
#         cbar.set_label('Flux Density [mJy/beam]')

#         ax.coords[0].set_axislabel('Right Ascension')
#         ax.coords[1].set_axislabel('Declination')
#         ax.coords[0].set_major_formatter('hh:mm')
#         ax.set_title("{0:s}".format(os.path.basename(fits_file_list[k])))

#         output = plot_name_list[k]

#         if plot_format == "pdf":
#             plt.savefig(output.replace(".png", ".pdf"),
#                         overwrite=True, bbox_inches='tight')
#         else:
#             plt.savefig(output, overwrite=True, bbox_inches='tight', dpi=400)

#         plt.close("all")

#     print("Plotting PyBDSF diagnostic plots. Done")


def qa_mosaic_run_pybdsf_validation(mosaic_name, qa_pybdsf_dir, output_name='', overwrite=True):
    """This function runs pybdsf on a mosaic image.

    It can also be used to run pybdsf on a single image.

    Note:
        The function assumes that the mosaic image is a fits file

    Parameter:
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
        run_pybdsf_validation_status : int
            Status of how well this function performed

    """

    # # change the working directory to where the qa directory
    # os.chdir(qa_pybdsf_dir)

    # # Create a link to the fits file so that the pybdsf log file is stored in the qa directory
    # image_name = os.path.basename(mosaic_name)

    # if not os.path.exists(image_name):
    #     os.symlink(mosaic_name, image_name)

    image_name = mosaic_name

    # try:
    #     os.symlink(mosaic_name, image_name)
    # except Exception e:
    #     return -1

    # # Check/create catalogue name
    # if output_name == '':
    #     cat_file = "{0:s}/{1:s}".format(
    #         qa_pybdsf_dir, os.path.basename(image_name).replace("fits", "_pybdsf_cat.fits"))
    # else:
    #     cat_file = output_name

    # assuming pybdsf will work
    run_pybdsf_validation_status = 1

    # Run pybdsf on the input image
    logging.info("#### Running pybdsf")
    try:

        # change into the directory where the QA products should be produced
        # This is necessary for the current implementation of the validation tool
        # Should it return to the initial directory?
        os.chdir(qa_pybdsf_dir)

        # run validation tool and pybdsf combined
        validation.run(image_name)

        # img = bdsf.process_image(image_name, quiet=True)
        # # img = bdsf.process_image(image_name, quiet=True, output_opts=True, plot_allgaus=True, plot_islands=True,
        # #                          savefits_meanim=True, savefits_normim=True, savefits_rankim=True, savefits_residim=True, savefits_rmsim=True)

        # # Write catalogue as csv file
        # logging.info("#### Writing catalogue")
        # img.write_catalog(outfile=cat_file, format='fits', clobber=True)

        # # Save plots
        # logging.info("#### Saving pybdsf plots")
        # plot_type_list = ['rms', 'mean',
        #                   'gaus_model', 'gaus_resid', 'island_mask']
        # fits_names = [cat_file.replace(
        #     ".fits", "_{0:s}.fits".format(plot)) for plot in plot_type_list]
        # plot_names = [fits.replace(
        #     ".fits", ".png") for fits in fits_names]
        # # plot_type_list = ['gaus_model', 'gaus_resid', 'island_mask']

        # # number of plots
        # n_plots = len(plot_type_list)

        # for k in range(n_plots):
        #     img.export_image(outfile=fits_names[k],
        #                      clobber=overwrite, img_type=plot_type_list[k])
    except Exception as e:
        logger.error(e)
        logger.error(
            "PyBDSF and validation tool failed on image {0:s}".format(image_name))
        run_pybdsf_validation_status = -1

    plot_type_list = ['rms', 'mean',
                      'gaus_model', 'gaus_resid', 'island_mask']
    fits_names = [image_name.replace(
        ".fits", "pybdsf_{0:s}.fits".format(plot)) for plot in plot_type_list]
    plot_names = [fits.replace(
        ".fits", ".png") for fits in fits_names]

    # add the continuum image
    fits_names.append(image_name)
    plot_names.append(os.path.basename(
        image_name).replace(".fits", ".png"))

    # create images without a lot of adjusting
    try:
        qa_plot_pybdsf_images(fits_names, plot_names)
    except Exception as e:
        logger.error(e)
        logger.error("Plotting PyBDSF diagnostic images failed")

    return run_pybdsf_validation_status

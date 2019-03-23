"""
This file contains functionality to analyze the quality of the data cube
generated by the pipeline for each beam.
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
from scipy.optimize import curve_fit

logger = logging.getLogger(__name__)


def gauss(x, *p):
    """Function to calculate a Gaussian value
    """
    A, mu, sigma = p
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))


def get_cube_stats(qa_line_dir, data_base_dir_list):
    """Function to get a simple rms per channel

    Parameter:
        qa_line_dir : str
            Directory where the line QA output is stored
        data_base_dir_list : list
            List of data directories on happili 1 to 4
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
                qa_line_beam_dir = "{0:s}/{1:s}".format(qa_line_dir, beam)

                # this directory does not exist create it
                if not os.path.exists(qa_line_beam_dir):
                    print("Creating directory {0:s}".format(qa_line_beam_dir))
                    os.mkdir(qa_line_beam_dir)

                # set the name of the of the cube file to analyze
                cube_file = "{0:s}/line/cubes/HI_image_cube.fits".format(
                    data_dir_beam)

                # make sure the cube file exists:
                if os.path.exists(cube_file):

                    # open fits file or at least try
                    try:
                        fits_hdulist = fits.open(cube_file)
                    except Exception as e:
                        logging.error(e)
                        continue

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

                    # creating an astropy table to store information about the cube
                    cube_info = Table([np.arange(n_channels), np.zeros(n_channels), np.zeros(
                        n_channels)], names=('channel', 'noise', 'gauss'))

                    # define range for histogram
                    histrange = np.arange(-0.5, 0.5, 0.0001)
                    # p0 is the initial guess for the fitting coefficients (A, mu and sigma above)
                    p0 = [1., 0., 0.001]

                    # This determines the noise in each channel, using standard rms and also by
                    # fitting the width of a histogram of image values.
                    # These give same results for now, but gauss fit could be improved by
                    # e.g. fitting only to part of histogram
                    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

                    for ch in range(n_channels):
                        # get rms
                        cube_info['noise'][ch] = np.std(cube[ch])
                        # determine histogram and fit gaussian
                        values = cube[ch]
                        histch, binedges = np.histogram(
                            values, bins=500, range=(-0.2, 0.2))
                        bin_centres = binedges[:-1] + np.diff(binedges) / 2
                        coeff, var_matrix = curve_fit(
                            gauss, bin_centres, histch, p0=p0)
                        # Get the fitted curve
                        hist_fit = gauss(bin_centres, *coeff)
                        # print 'Fitted mean = ', coeff[1]
                        # print 'Fitted standard deviation = ', coeff[2]
                        cube_info['gauss'][ch] = coeff[2]

                    # write noise data
                    cube_info.write(
                        "{0:s}/beam_{1:s}_cube_noise_info.csv".format(qa_line_beam_dir, beam), format="csv", overwrite=True)

                    # Create plot
                    # +++++++++++
                    ax = plt.subplot(projection=wcs)

                    # plot data and fit
                    ax.plot(
                        cube_info['channel'], cube_info['noise'] / 1.e3, color='blue', linestyle='-')
                    ax.plot(cube_info['channel'], cube_info['gauss'] /
                            1.e3, color='orange', linestyle='--')

                    # add axes labels
                    ax.title('Beam {0:s}'.format(beam))
                    ax.xlabel('Channel number')
                    ax.ylabel('Noise (mJy/beam)')
                    ax.set_xlim([0, n_channels-1])

                    # add second axes with frequency
                    ax_x2 = ax.twiny()

                    # get frequency for first and last channel
                    # freq_ticks = np.array(
                    #     [wcs.wcs_pix2world([[0, 0, xtick]], 1)[0, 2]] for xtick in ax.get_xticks())
                    freq_first_ch = wcs.wcs_pix2world([[0, 0, 0]], 1)[0, 2]
                    freq_last_ch = wcs.wcs_pix2world(
                        [[0, 0, n_channels]], 1)[0, 2]
                    ax_x2.set_xlim([freq_first_ch/1.e6, freq_last_ch/1.e6])
                    ax_x2.xlabel("Frequency [MHz]")

                    # add legend
                    ax.plot([0.63, 0.68], [0.95, 0.95], transform=ax.transAxes,
                            color='blue', linestyle='-')
                    ax.annotate('Data', xy=(0.7, 0.95), xycoords='axes fraction',
                                va='center', ha='left', color='red')

                    ax.plot([0.63, 0.68], [0.9, 0.9], transform=ax.transAxes,
                            color='blue', linestyle='-')
                    ax.annotate('Fit', xy=(0.7, 0.9), xycoords='axes fraction',
                                va='center', ha='left', color='blue')

                    ax_x2.tick_params(axis='both', bottom='off', top='on',
                                      left='on', right='on', which='major', direction='in')

                    ax.tick_params(axis='both', bottom='on', top='off', left='on', right='on',
                                   which='major', direction='in')

                    plt.savefig(
                        '{0:s}/beam_{1:s}_cube_noise.png'.format(qa_line_beam_dir, beam), dpi=300)
                    plt.close('all')

                    # close fits file
                    fits_hdulist

                    logging.info("Finished analyzing beam {0:s} ({1:.1f}s)".format(
                        beam, time.time()-start_time_beam))
                else:
                    logging.warning(
                        "No HI cube found for beam {0:s}".format(beam))

            logging.info("Finished going through data directory {0:s} ({1:.1f}s)".format(
                data_dir, time.time()-start_time_data))

        else:
            logging.warning("No beams found in {0:s}".format(data_dir))

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
import glob
from dataqa.scandata import get_default_imagepath

import matplotlib.pyplot as plt
# from scipy.optimize import curve_fit

logger = logging.getLogger(__name__)


# def gauss(x, *p):
#    """Function to calculate a Gaussian value
#    """
#    A, mu, sigma = p
#    return A*np.exp(-(x-mu)**2/(2.*sigma**2))

def combine_cube_stats(obs_id, qa_line_dir):
    """
    Function to combine the statistic information from all cubes
    """

    logger.info("Collecting cube statistics")

    host_name = socket.gethostname()

    # output file name
    table_file_name = os.path.join(
        qa_line_dir, "{}_HI_cube_noise_statistics.ecsv".format(obs_id))

    # list of data directories
    qa_line_dir_list = [qa_line_dir, qa_line_dir.replace(
        "/data/", "/data2/"), qa_line_dir.replace("/data/", "/data3/"), qa_line_dir.replace("/data/", "/data4/")]

    # total number of expected beams
    # catching the host should make it work on other happilis, too
    if host_name == "happili-01":
        n_beams = 40
    else:
        happili_number = int(host_name.split("-")[-1])
        n_beams = 10 * happili_number

    # total number of cubes
    n_cubes = 8

    # define table columns
    # this column will hold the beam number
    beam = np.full(n_cubes * n_beams, -1)
    # this one will specify the cube
    cube = np.full(n_cubes * n_beams, -1)
    # this one will store the median rms
    median_rms = np.full(n_cubes * n_beams, -1.)
    # this one will store the mean rms
    mean_rms = np.full(n_cubes * n_beams, -1.)
    # this one will store the min rms
    min_rms = np.full(n_cubes * n_beams, -1.)
    # this one will store the max rms
    max_rms = np.full(n_cubes * n_beams, -1.)
    # percentile below a limit of 2mJy/beam and 3mJy/beam
    percentile_rms_below_2mJy = np.full(n_cubes * n_beams, -1.)
    percentile_rms_below_3mJy = np.full(n_cubes * n_beams, -1.)
    percentile_rms_below_4mJy = np.full(n_cubes * n_beams, -1.)

    # now go through the different cubes
    for cube_counter in range(n_cubes):

        logger.info(
            "Processing noise information for cube {}".format(cube_counter))

        # now go through the data directories and get the cube files
        for dir_counter in range(len(qa_line_dir_list)):
            line_dir = qa_line_dir_list[dir_counter]

            cube_list = glob.glob(os.path.join(
                line_dir, "[0-3][0-9]/*cube{0:d}_info.csv"))

            # in case there are no such cubes, fill only beam and cube column
            if len(cube_list) == 0:
                logger.warning("No cube files found in {}".format(line_dir))
                # only 10 beams, because there are 4 happili directories
                # here beam_counter is only the last digit in the beam number
                for beam_counter in range(10):
                    table_index = n_beams * cube_counter + 10 * dir_counter + beam_counter
                    beam[table_index] = 10 * dir_counter + beam_counter
                    cube[table_index] = cube_counter
            # if there are cubes, go through them
            else:
                cube_list.sort()
                for file_counter in range(len(cube_list)):
                    cube_file = cube_list[file_counter]
                    # read in the file
                    cube_data = Table.read(cube_file, format="ascii.csv")
                    # get only the non-nan values
                    noise = cube_data['noise'][np.isnan(
                        cube_data['noise']) == False]
                    # the beam number is part of the file name
                    beam_nr = int(os.path.basename(cube_file).split("_")[1])
                    # get the table index based on the beam numbder
                    table_index = n_beams * cube_counter + beam_nr
                    beam[table_index] = beam_nr
                    cube[table_index] = cube_counter

                    median_rms[table_index] = np.nanmedian(noise)
                    mean_rms[table_index] = np.nanmean(noise)
                    min_rms[table_index] = np.nanmin(noise)
                    max_rms[table_index] = np.nanmax(noise)

                    percentile_rms_below_2mJy = np.size(
                        np.where(noise < 0.002)[0]) / np.size(noise)
                    percentile_rms_below_3mJy = np.size(
                        np.where(noise < 0.003)[0]) / np.size(noise)
                    percentile_rms_below_4mJy = np.size(
                        np.where(noise < 0.004)[0]) / np.size(noise)

        logger.info(
            "Processing noise information for cube {} ... Done".format(cube_counter))

    # create the table
    cube_summary = Table([beam, cube, median_rms, mean_rms, min_rms, max_rms, percentile_rms_below_2mJy, percentile_rms_below_3mJy, percentile_rms_below_4mJy], names=(
        'beam', 'cube', 'median_rms', 'mean_rms', 'min_rms', 'max_rms', 'precentile_rms_below_2mJy', 'precentile_rms_below_3mJy', 'precentile_rms_below_4mJy'))

    cube_summary.write(table_file_name, format="ascii.ecsv")

    logger.info(
        "Collecting cube statistics ... Done. Saving to {}".format(table_file_name))


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

        logger.info("## Going through the beams in {0:s}".format(data_dir))

        # getting a list of beams
        data_dir_beam_list = glob.glob("{0:s}/[0-3][0-9]".format(data_dir))

        # checking whether no beam was found
        if len(data_dir_beam_list) != 0:

            # sort beam list
            data_dir_beam_list.sort()

            start_time_beam = time.time()

            # going through all the beams that were found
            # +++++++++++++++++++++++++++++++++++++++++++
            for data_dir_beam in data_dir_beam_list:

                # getting the beam
                beam = os.path.basename(data_dir_beam)

                logger.info("Analyzing beam {0:s}".format(beam))

                # setting the output directory for the beam
                qa_line_beam_dir = "{0:s}/{1:s}".format(qa_line_dir, beam)

                # this directory does not exist create it
                if not os.path.exists(qa_line_beam_dir):
                    logger.info(
                        "Creating directory {0:s}".format(qa_line_beam_dir))
                    os.mkdir(qa_line_beam_dir)

                # set the name of the of the cube file to analyze
                cube_file = "{0:s}/line/cubes/HI_image_cube.fits".format(
                    data_dir_beam)

                # there are several cubes
                cube_file_list = glob.glob(cube_file.replace("cube", "cube*"))

                # continue only if glob has found cubes
                if len(cube_file_list) != 0:

                    cube_file_list.sort()

                    for cube_file in cube_file_list:

                        # open fits file or at least try
                        try:
                            fits_hdulist = fits.open(cube_file)
                        except Exception as e:
                            logger.exception(e)
                            continue

                        logger.info(
                            "Getting statistics for cube {}".format(cube_file))

                        # get wcs object
                        wcs = WCS(fits_hdulist[0].header)

                        # getting rid of stokes axis and check that it is a cube
                        if wcs.naxis == 4:
                            wcs = wcs.dropaxis(3)
                            cube = fits_hdulist[0].data[0]
                        elif wcs.naxis == 3:
                            cube = fits_hdulist[0].data
                        else:
                            logger.warning(
                                "Fits file {0:s} is not a cube".format(cube_file))
                            continue

                        # get the shape of the cube
                        cube_shape = np.shape(cube)

                        # get the number of channels
                        n_channels = cube_shape[0]

                        # creating an astropy table to store information about the cube
                        cube_info = Table([np.arange(n_channels), np.zeros(
                            n_channels)], names=('channel', 'noise'))

                        # define range for histogram
                        # histrange = np.arange(-0.5, 0.5, 0.0001)
                        # p0 is the initial guess for the fitting coefficients (A, mu and sigma above)
                        # p0 = [1., 0., 0.001]

                        # This determines the noise in each channel, using standard rms and also by
                        # fitting the width of a histogram of image values.
                        # These give same results for now, but gauss fit could be improved by
                        # e.g. fitting only to part of histogram
                        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

                        for ch in range(n_channels):
                            # get rms
                            cube_info['noise'][ch] = np.std(cube[ch])
                            # determine histogram and fit gaussian
                            # values = cube[ch]
                            # histch, binedges = np.histogram(
                            #    values, bins=500, range=(-0.2, 0.2))
                            # bin_centres = binedges[:-1] + np.diff(binedges) / 2
                            # coeff, var_matrix = curve_fit(
                            #    gauss, bin_centres, histch, p0=p0)
                            # Get the fitted curve
                            # hist_fit = gauss(bin_centres, *coeff)
                            # print 'Fitted mean = ', coeff[1]
                            # print 'Fitted standard deviation = ', coeff[2]
                            # cube_info['gauss'][ch] = coeff[2]

                        # write noise data
                        cube_info.write(
                            "{0:s}/beam_{1:s}_{2:s}_info.csv".format(qa_line_beam_dir, beam, os.path.basename(cube_file).rstrip(".fits").split("_")[-1]), format="csv", overwrite=True)

                        themedian = np.nanmedian(cube_info['noise'])
                        # print("Median is " + str(round(themedian*1000, 2)) + " mJy")

                        # Create plot
                        # +++++++++++
                        ax = plt.subplot(111)

                        # plot data and fit
                        ax.plot(
                            cube_info['channel'], cube_info['noise'] * 1.e3, color='blue', linestyle='-')
                        # ax.plot(cube_info['channel'], cube_info['gauss'] *
                        #        1.e3, color='orange', linestyle='--')

                        # add axes labels
                        ax.set_xlabel('Channel number')
                        ax.set_ylabel('Noise (mJy/beam)')
                        ax.set_xlim([0, n_channels-1])

                        # add second axes with frequency
                        ax_x2 = ax.twiny()

                        # get frequency for first and last channel
                        # freq_ticks = np.array(
                        #     [wcs.wcs_pix2world([[0, 0, xtick]], 1)[0, 2]] for xtick in ax.get_xticks())
                        freq_first_ch = wcs.wcs_pix2world([[0, 0, 0]], 1)[0, 2]
                        freq_last_ch = wcs.wcs_pix2world(
                            [[0, 0, n_channels-1]], 1)[0, 2]
                        ax_x2.set_xlim([freq_first_ch/1.e6, freq_last_ch/1.e6])

                        ax_x2.set_xlabel("Frequency [MHz]")

                        # add legend
                        ax.plot([0.73, 0.78], [0.95, 0.95], transform=ax.transAxes,
                                color='blue', linestyle='-')
                        ax.annotate('Data', xy=(0.8, 0.95), xycoords='axes fraction',
                                    va='center', ha='left', color='blue')

                        # ax.plot([0.73, 0.78], [0.9, 0.9], transform=ax.transAxes,
                        #        color='orange', linestyle='--')
                        ax.annotate('Median = %s mJy' % (str(round(themedian*1000, 2))), xy=(0.05, 0.9), xycoords='axes fraction',
                                    va='center', ha='left', color='orange')

                        ax_x2.tick_params(axis='both', bottom='off', top='on',
                                          left='on', right='on', which='major', direction='in')

                        ax.tick_params(axis='both', bottom='on', top='off', left='on', right='on',
                                       which='major', direction='in')

                        plt.savefig(
                            '{0:s}/beam_{1:s}_{2:s}_noise.png'.format(qa_line_beam_dir, beam, os.path.basename(cube_file).rstrip(".fits").split("_")[-1]), dpi=300)
                        plt.close('all')

                        # close fits file
                        fits_hdulist

                        logger.info("Finished analyzing cube {0:s}".format(
                            cube_file))
                else:
                    logger.warning(
                        "No HI cube found for beam {0:s}".format(beam))

                logger.info("Finished analyzing beam {0:s} ({1:.1f}s)".format(
                            beam, time.time()-start_time_beam))

            logger.info("Finished going through data directory {0:s} ({1:.1f}s)".format(
                data_dir, time.time()-start_time_data))

        else:
            logger.warning("No beams found in {0:s}".format(data_dir))

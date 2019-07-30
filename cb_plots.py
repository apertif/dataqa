# Compound beam overview plots of QA

from __future__ import print_function

__author__ = "E.A.K. Adams"

"""
Functions for producing compound beam plots
showing an overview of data QA

Contributions from R. Schulz
"""

from astropy.io import ascii
from astropy.table import Table
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import numpy as np
import os
import logging
import pkg_resources

logger = logging.getLogger(__name__)

"""
Globally define beam plotting parameters
So they are updated in one place
"""

radius = 0.2  # radius of beam to plot, in degrees
plotrange = [1.75, -1.75, -1.75, 1.4]  # range to plot, RA runs backwards
offset_beam0_x = 1.5
offset_beam0_y = -1.5


def make_cb_plots_for_report(obs_id, qa_dir, plot_dir=None):
    """
    Function to create the different cb plots for the web report.

    The function currently creates the following plots
    - phase selfcal done
    - amplitude selfcal done
    - continuum rms (range: 10-50 muJy/beam)
    - continuum minor axis (range: 10-15 arcsec)

    Args:
        obs_id (int): ID of observation
        qa_dir (str): Path to QA directory of the observation
        plot_dir (str): Optional directory for the plots
    """

    logger.info("Creating summary cb plots")

    # Create a directory to put all the plots in
    if plot_dir is None:
        cb_plot_dir = os.path.join(qa_dir, "cb_plots")
    else:
        cb_plot_dir = plot_dir

    if not os.path.exists(cb_plot_dir):
        os.mkdir(cb_plot_dir)
        logger.info("Creating directory {}".format(cb_plot_dir))
    else:
        logger.info("Directory {} already exists".format(cb_plot_dir))

    # get path for cboffset file
    package_name = __name__
    file_name = 'cb_offsets.txt'
    cboffsets_file = pkg_resources.resource_filename(
        package_name, file_path)
    logger.info(
        "Using file {0} for compound beam offsets".format(cboffsets_file))

    # first create the compound beam plot
    logger.info("Plotting compound beams")
    output_dir = cb_plot_dir
    plot_name = "{}_cb_overview".format(obs_id)
    make_cb_beam_plot(outputdir=output_dir, outname=plot_name,
                      cboffsets=cboffsets_file)
    logger.info("Plotting compound beams ... Done")

    # Create selfcal plots
    logger.info("Creating cb plot for selfcal")
    selfcal_summary_file = os.path.join(
        qa_dir, "selfcal/{}_selfcal_summary.csv".format(obs_id))
    if os.path.exists(selfcal_summary_file):
        # first plot phase selfcal
        plot_name = "{}_selfcal_phase".format(obs_id)
        make_cb_plot_value(selfcal_summary_file, "targetbeams_phase_status",
                           boolean=True, outputdir=output_dir, outname=plot_name, cboffsets=cboffsets_file)

        # now plot amplitude selfcal
        plot_name = "{}_selfcal_amp".format(obs_id)
        make_cb_plot_value(selfcal_summary_file, "targetbeams_amp_status",
                           boolean=True, outputdir=output_dir, outname=plot_name, cboffsets=cboffsets_file)
        logger.info("Creating cb plot for selfcal ... Done")
    else:
        logger.warning("Could not find {}".format(selfcal_summary_file))
        logger.info("Creating cb plot for selfcal ... Failed")

    # Create continuum plots
    logger.info("Creating cb plot for continuum")
    continuum_summary_file = os.path.join(
        qa_dir, "continuum/{}_combined_continuum_image_properties.csv".format(obs_id))
    if os.path.exists(continuum_summary_file):
        # plot rms
        plot_name = "{}_continuum_rms".format(obs_id)
        make_cb_plot_value(continuum_summary_file, "RMS",
                           goodrange=[10, 50], outputdir=output_dir, outname=plot_name, cboffsets=cboffsets_file)

        # plot minor beam axis
        plot_name = "{}_continuum_beam_min".format(obs_id)
        make_cb_plot_value(continuum_summary_file, "BMIN",
                           goodrange=[10, 15], outputdir=output_dir, outname=plot_name, cboffsets=cboffsets_file)
        logger.info("Creating cb plot for continuum ... Done")
    else:
        logger.warning("Could not find {}".format(continuum_summary_file))
        logger.info("Creating cb plot for continuum ... Failed")

    # Create line plots
    logger.info("Creating cb plots for line")
    line_summary_file = os.path.join(
        qa_dir, "line/{}_HI_cube_noise_statistics.ecsv".format(obs_id))
    if os.path.exists(line_summary_file):
        # read the file
        line_summary_data = Table.read(line_summary_file, format="ascii.ecsv")

        # number of cubes
        n_cubes = np.size(np.unique(line_summary_data['cube']))

        # go through the cubes and create plots for each one
        for cube_counter in range(n_cubes):
            logger.info("Plotting cube {}".format(cube_counter))

            cube_data = line_summary_data[np.where(
                line_summary_data['cube'] == cube_counter)]

            # remove non-existing beams
            cube_data['median_rms'][np.where(
                cube_data['median_rms'] == -1)] = np.nan

            # convert median rms into mJy
            cube_data['median_rms'] *= 1.e3

            # plot name
            plot_name = "{0}_HI_median_rms_cube{1}".format(
                obs_id, cube_counter)
            # use a different range of good values for
            if cube_counter < 7:
                goodrange = [0, 2]
            else:
                goodrange = [0, 3]
            make_cb_plot_value(cube_data, "median_rms",
                               goodrange=goodrange, outputdir=output_dir, outname=plot_name, cboffsets=cboffsets_file)

        logger.info("Creating cb plot for line ... Done")
    else:
        logger.warning("Could not find {}".format(line_summary_file))
        logger.info("Creating cb plot for line ... Failed")

    logger.info("Creating summary cb plots ... Done")


def make_cb_beam_plot(cboffsets='cb_offsets.txt',
                      outputdir=None, outname=None):
    """
    This function specifically makes a plot of only
    the compound beams, labelling and numbering them
    """
    # get paths and names set
    if outname is None:
        outname = 'CB_overview'
    if outputdir is not None:
        outpath = os.path.join(outputdir, outname)
    else:
        outpath = outname  # write to current directory
    # get the beams
    cbpos = ascii.read(cboffsets)
    # open figure
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.axis(plotrange)  # RA axis runs backwards
    # set up beams
    beams = np.arange(len(cbpos))
    r = radius  # beam size
    for i, (x1, y1) in enumerate(zip(cbpos['ra'], cbpos['dec'])):
        if i == 0:
            # offset beam 0
            x1 = offset_beam0_x
            y1 = offset_beam0_y
        # set circle
        circle = Circle((x1, y1), r, color='blue', alpha=0.4)
        fig.gca().add_artist(circle)
        # beams.append(circle)
        # write text with value
        ax.text(x1, y1, ('CB{0:02}').format(beams[i]),
                horizontalalignment='center',
                verticalalignment='center', size=18,
                fontweight='medium')
    # p=PatchCollection(beams, alpha=0.4)
    # ax.add_collection(p)
    ax.set_xlabel('RA offset, deg', size=15)
    ax.set_ylabel('Dec offset, deg', size=15)
    ax.set_title('{}'.format(outname), fontweight='medium', size=24)
    plt.savefig('{}.png'.format(outpath), overwrite=True,
                bbox_inches='tight', dpi=200)


def make_cb_plot_value(filename, column, goodrange=None,
                       boolean=False, cboffsets='cb_offsets.txt',
                       outputdir=None, outname=None):
    """
    Take a csv file or a table object and produce the plots
    Provide the column name to plot
    Optionally provide a range of good values that
    will have beams plotted in green
    Or set boolean=True to plot colors based on a boolean value
    Lack of data in plotted in grey
    Default is to plot as red
    Color scheme should be updated to
    take into account colorblindness
    """
    # check if file name is a string
    if type(filename) == str:
        # read the csv file
        table = ascii.read(filename, format='csv')
    # otherwise assume a table object as been given
    else:
        table = filename
    # print(table.colnames)
    # check that column name exists:
    if column in table.colnames:
        pass
    else:
        # select a column, assume first column is beams
        print(('Warning! Column name {0} not found.'
               ' Using third column of csv, {1} as default.'.format(column,
                                                                    table.colnames[2])))
        column = table.colnames[2]
    # gets paths and names set
    if outname is None:
        outname = column
    if outputdir is not None:
        outpath = "{0}/{1}".format(outputdir, outname)
    else:
        outpath = outname  # write to current directory
    # check automatically if a column is boolean
    if (table[column][0]) == 'False' or (table[column][0] == 'True'):
        boolean = True
    # make an array to hold colors:
    colors = np.full(40, 'r')
    # colors = np.array(['r' for k in range(40)])
    # find empty beams
    # not all tables have this so do as try/except
    try:
        # 'exist' column is read as strings
        nanind = np.where(table['exist'] == 'False')[0]
        colors[nanind] = 'k'
    except:
        # assume that the columns have NaNs
        if table[column].dtype == np.float64:
            nanind = np.where(np.isnan(table[column]) == True)[0]
            colors[nanind] = 'k'
    # find "good" values
    if goodrange != None:
        if len(goodrange) == 2:
            # first turn good data into floats:
            goodind = np.where(np.logical_and(table[column] >= goodrange[0],
                                              table[column] <= goodrange[1]))[0]
            # goodind = np.where(table[column]>=goodrange[0])[0]
            # print(goodind)
            colors[goodind] = 'green'
    if boolean == True:
        # assume column array is true/false
        # find trues and make green
        goodind = np.where(table[column] == 'True')[0]
        colors[goodind] = 'green'
        # in this case, also make sure to overwrite anything done by exist column
        badind = np.where(table[column] == 'False')[0]
        colors[badind] = 'red'
    # get the beams
    cbpos = ascii.read(cboffsets)
    # open figure
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.axis(plotrange)  # RA axis runs backwards
    # set up beams
    beams = []
    r = radius  # beam size
    for i, (x1, y1) in enumerate(zip(cbpos['ra'], cbpos['dec'])):
        if i == 0:
            # offset beam 0
            x1 = offset_beam0_x
            y1 = offset_beam0_y
        # set circle
        circle = Circle((x1, y1), r, color=colors[i], alpha=0.4)
        fig.gca().add_artist(circle)
        # beams.append(circle)

        # only add text if the color is not grey:
        if colors[i] != 'k':
            # write text with value
            value = table[column][i]
            if type(value) == float or type(value) == np.float64:
                value_label = "{0:.1f}".format(value)
            else:
                value_label = str(value)
            ax.text(x1, y1, ('{0}').format(value_label),
                    horizontalalignment='center',
                    verticalalignment='center', size=18,
                    fontweight='medium')
    # p=PatchCollection(beams, alpha=0.4)
    # ax.add_collection(p)
    ax.set_xlabel('RA offset, deg', size=15)
    ax.set_ylabel('Dec offset, deg', size=15)
    ax.set_title('{}'.format(outname), size=24, fontweight='medium')
    plt.savefig('{}.png'.format(outpath), overwrite=True,
                bbox_inches='tight', dpi=200)

# Module with functionality to get the inspection plots for an Apertif observation

import numpy as np
import os
import glob
import logging
import subprocess

logger = logging.getLogger(__name__)

FNULL = open(os.devnull, 'w')


def get_inspection_plot_list(is_calibrator=False):
    """
    Function to return a list of inspection plot

    This list only contains the type of inspection plot
    to be copied from ALTA.

    Args:
        polarisation (str): Polarisation, currently XX only

    Return:
        (List(str)): List of inspection plots

    """
    if is_calibrator:
        plot_type_list = ['_beams_xx',
                          '_beams_yy']
    else:
        plot_type_list = ['_beams_ampvstime_XX',
                          '_beams_ampvschan_XX',
                          '_beams_phavstime_XX',
                          '_beams_phavschan_XX',
                          '_beams_waterfall_amplitude_autoscale_XX',
                          '_beams_waterfall_amplitude_noscale_XX',
                          '_beams_waterfall_phase_autoscale_XX',
                          '_beams_waterfall_phase_noscale_XX',
                          '_beams_xx',
                          '_beams_yy']

    return plot_type_list


def get_inspection_plot_from_alta(qa_plot_dir, obs_id, plot_type_list):
    """
    Function to get a specific inspection plot from ALTA

    Args:
        qa_plot_dir (str): Directory where plots should be stored
        obs_id (int): ID of the observation (scan number or task_id)
        plot_type (str): Type of inspection plot

    Return:
        plot_file_name (str): Name of the plot (without alta path)
    """

    # Main ALTA path
    default_alta_path = "/altaZone/archive/apertif_main/visibilities_default/"

    # Path of inspection plots on ALTA for a given obs id
    alta_plot_path = os.path.join(default_alta_path, "{}_INSP".format(obs_id))

    plot_file_name_list = ["WSRTA{0}{1}.png".format(
        obs_id, plot_type) for plot_type in plot_type_list]

    alta_plot_file_list = [os.path.join(
        alta_plot_path, plot_file_name) for plot_file_name in plot_file_name_list]

    alta_files = " ".join(alta_plot_file_list)

    # set the irod files location
    irods_status_file = os.path.join(
        qa_plot_dir, "{}_insp-icat.irods-status".format(obs_id))

    irods_status_lf_file = os.path.join(
        qa_plot_dir, "{}_insp-icat.lf-irods-status".format(obs_id))

    # iget command to get the plot
    try:
        cmd = "iget -rfPIT -X {0} --lfrestart {1} --retries 5 {2} {3}".format(
            irods_status_file, irods_status_lf_file, alta_files, qa_plot_dir)
        logger.debug(cmd)
        subprocess.check_call(cmd, shell=True, stdout=FNULL, stderr=FNULL)
    except Exception as e:
        logger.warning(
            "Failed retrieving inpsection plots for {}".format(obs_id))
        logger.exception(e)
    else:
        logger.info(
            "Successully retrieved inspection plots for {}".format(obs_id))

    # iget -rfPIT -X /data/schulz/transfer_files/test-icat.irods-status --lfrestart /data/schulz/transfer_files/test-icat.lf-irods-status --retries 5 /altaZone/home/apertif_main/early_results/temp_storage/190725042/17/M0155+3130.UVFITS /data/schulz

    # return full path
    # plot_file_name_with_path = os.path.join(qa_plot_dir, plot_file_name)

    return plot_file_name_list


def rename_inspection_plots(qa_plot_dir, plot_file_name_list):
    """
    Function to rename the inspection plots from the target so that 
    they stay in order.
    """

    plot_counter = 1

    for plot_file_name in plot_file_name_list:
        # rename it to keep the order
        plot_file_name_new = os.path.join(qa_plot_dir, "{0:02d}_{1:s}".format(
            plot_counter, plot_file_name))

        # have to add the path to the original plot name now
        plot_file_name = os.path.join(qa_plot_dir, plot_file_name)

        try:
            os.rename(plot_file_name, plot_file_name_new)
        except Exception as e:
            logger.warning("Renaming {} failed".format(plot_file_name))
            logger.exception(e)
        else:
            logger.info("Inspection plot saved as {0:s}".format(
                os.path.basename(plot_file_name_new)))

        plot_counter += 1


def get_inspection_plots(obs_id, qa_plot_dir, is_calibrator=False, cal_id=None):
    """
    Function to get all inspection plots from ALTA useful for the QA

    Args:
        qa_plot_dir (str) Directory where plots should be stored
        obs_id (int) ID of observation (scan number or task id)
    """

    # list of types of inspection plots
    plot_type_list = get_inspection_plot_list(is_calibrator=is_calibrator)

    # get inspection plot
    if cal_id is None:
        plot_file_name_list = get_inspection_plot_from_alta(
            qa_plot_dir, obs_id, plot_type_list)

        rename_inspection_plots(qa_plot_dir, plot_file_name_list)
    else:
        plot_file_name_list = get_inspection_plot_from_alta(
            qa_plot_dir, cal_id, plot_type_list)

# Module with functionality to get the inspection plots for an Apertif observation

import numpy as np
import os
import glob
import logging
import subprocess

logger = logging.getLogger(__name__)

FNULL = open(os.devnull, 'w')


def get_inspection_plot_list(polarisation='XX'):
    """
    Function to return a list of inspection plot 

    This list only contains the type of inspection plot
    to be copied from ALTA.

    Args:
        polarisation (str): Polarisation, currently XX only

    Return:
        (List(str)): List of inspection plots

    """
    plot_type_list = ['_beams_ampvstime',
                      '_beams_ampvschan',
                      '_beams_phavstime',
                      '_beams_phavschan',
                      '_beams_waterfall_amplitude_autoscal',
                      '_beams_waterfall_amplitude_noscal',
                      '_beams_waterfall_phase_autoscal',
                      '_beams_waterfall_amplitude_noscal',
                      '_beams_xx',
                      '_beams_yy']

    return plot_type_list


def get_inspection_plots(qa_plot_dir, obs_id, plot_type):
    """
    Function to get the inspection plot from ALTA

    Args:
        obs_id (int): ID of the observation (scan number or task_id)
        plot_type (str): Type of inspection plot

    """

    # Main ALTA path
    default_alta_path = "/altaZone/archive/apertif_main/visibilities_default/"

    # Path of inspection plots on ALTA for a given obs id
    alta_plot_path = os.path.join(default_alta_path, "{}_INSP".format(obs_id))

    plot_file_name = "WSRTA{0}{1}.png".format(obs_id, plot_type)

    alta_plot_file = os.path.join(alta_plot_path, plot_file_name)

    # iget command to get the plot
    try:
        cmd = "iget -fPIT -X --retries 5 {0} {1}".format(
            alta_plot_file, qa_plot_dir)
        logger.debug(cmd)
        subprocess.check_call(cmd, shell=True, stdout=FNULL, stderr=FNULL)
    except Exception as e:
        logger.warning("Failed retrieving {}".format(alta_plot_file))
        logger.exception(e)
    else:
        logger.info("Successully retrieved {}".format(alta_plot_file))

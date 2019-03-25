"""
This script contains functionality to read the selfcal report
"""

import os
from apercal.libs import lib
from apercal.modules.scal import scal
import glob
import socket
import logging
from astropy.io import fits
from astropy.wcs import WCS

logger = logging.getLogger(__name__)


def get_selfcal_maps(obs_id, target, qa_selfcal_dir):
    """
    This function reads the selfcal report for every beam.

    It will convert the miriad images temporarily into fits. The fits files
    will be delelted afterwards.
    At the moment only the image and residual is taken into account.
    """

    # check host name
    host_name = socket.gethostname()

    if host_name != "happili-01":
        logger.warning("You are not working on happili-01.")
        logger.warning("The script will not process all beams")
        logger.warning("Please switch to happili-01")

    # get a list of data beam directories
    param_file_list = glob.glob(
        "/data*/apertif/{0:s}/param_[0-3][0-9]".format(obs_id))

    if len(param_file_list) != 0:

        param_file_list.sort()

        # go through the beam directories found
        for param_file in param_file_list:

            logger.info(
                "## Getting selfcal report for {0:s}".format(param_file))

            beam = param_file.split("/")[-1]

            # create beam directory in selfcal QA dir
            qa_selfcal_beam_dir = "{0:s}{1:s}".format(qa_selfcal_dir, beam)

            if not os.path.exists(qa_selfcal_beam_dir):
                os.mkdir(qa_selfcal_beam_dir)

            # read parameter file
            param = np.load(param_file)

            # get selfcal task and set directory
            task = scal()
            scal.basedir = param_file.replace(os.path.basename(param_file))
            scal.name = "{0:s}.MS".format(target)

            html_file = "{0:s}/{2:s}".format(qa_selfcal_beam_dir,
                                             os.path.basename(param_file)).replace(".log", ".html")

            try:
                report = p.summary()
                report.to_html(html_file)
            except Exception as e:
                logger.error(e)

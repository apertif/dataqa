"""
This module containes functionality to read the timing
measurement of the pipeline for the report
"""

import logging
import os
from astropy.table import Table
from apercal import parselog
from dataqa.scandata import get_default_imagepath
import socket

logger = logging.getLogger(__name__)


def get_pipeline_run_time(obs_id):
    """Function to get the run time of apercal parts
    """
    logger.info("## Reading apercal timing measurements")

    # get the QA path
    qa_dir = get_default_imagepath(obs_id)

    host_name = socket.gethostname()

    if host_name == "happili-01":
        apercal_log_list = ["{0:s}apercal.log".format(qa_dir).replace(
            "qa/", ""), "{0:s}apercal.log".format(qa_dir).replace("qa/", "").replace("/data", "/data2"), "{0:s}apercal.log".format(qa_dir).replace("qa/", "").replace("/data", "/data3"), "{0:s}apercal.log".format(qa_dir).replace("qa/", "").replace("/data", "/data4")]
        host_name_list = ["happili-01",
                          "happili-02", "happili-03", "happili-04"]
    else:
        apercal_log_list = ["{0:s}apercal.log".format(qa_dir).replace(
            "qa/", "")]
        host_name_list = [host_name]

    # Create an apercal QA directory
    qa_apercal_dir = "{0:s}apercal_performance/".format(qa_dir)

    if not os.path.exists(qa_apercal_dir):
        logger.info("Creating directory {0:s}".format(qa_apercal_dir))
        try:
            os.mkdir(qa_apercal_dir)
        except Exception as e:
            logger.error(e)

    # go through the list of apercal directories
    for log_counter in range(len(apercal_log_list)):

        if os.path.exists(apercal_log_list[log_counter]):
            logger.info(
                "Reading out timing measurement for {0:s}".format(apercal_log_list[log_counter]))

            # read timing information
            timinginfo = parselog(apercal_log_list[log_counter])

            # make it an astropy Table
            timinginfo_table = Table(
                rows=timinginfo, names=('pipeline_step', 'run_time'))

            table_output_name = "{0:s}{1:s}".format(qa_apercal_dir, os.path.basename(apercal_log_list[log_counter])).replace(
                ".log", "_{0:s}.csv".format(host_name_list[log_counter]))

            try:
                timinginfo_table.write(table_output_name, format="csv")
            except Exception as e:
                logger.error(e)
        else:
            logger.warning(
                "Could not find {0:s}".format(apercal_log_list[log_counter]))

    logger.info("## Reading apercal timing measurements. Done")

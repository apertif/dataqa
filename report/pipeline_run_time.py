"""
This module containes functionality to read the timing
measurement of the pipeline for the report
"""

import logging
import os
from astropy.table import Table, hstack, vstack
from apercal import parselog
from scandata import get_default_imagepath
import socket
import numpy as np
import glob
from datetime import timedelta

logger = logging.getLogger(__name__)


def get_pipeline_run_time(obs_id, trigger_mode=False):
    """Function to get the run time of apercal parts

    Since parselog is broken and the apercal logfiles have changed
    due to the parallelisation, this script just reads out the information
    from the main logfile
    """
    logger.info("## Reading apercal timing measurements")

    # get the QA path
    qa_dir = get_default_imagepath(obs_id)

    host_name = socket.gethostname()

    if trigger_mode:
        data_dir_list = [qa_dir.replace("qa/", "")]
        host_name_list = [host_name]
    elif host_name == "happili-01" and not trigger_mode:
        data_dir_list = [qa_dir.replace(
            "qa/", ""), qa_dir.replace("qa/", "").replace("/data", "/data2"), qa_dir.replace("qa/", "").replace("/data", "/data3"), qa_dir.replace("qa/", "").replace("/data", "/data4")]
        host_name_list = ["happili-01",
                          "happili-02", "happili-03", "happili-04"]
    else:
        data_dir_list = [qa_dir.replace("qa/", "")]
        host_name_list = [host_name]

    # Create an apercal QA directory
    qa_apercal_dir = "{0:s}apercal_performance/".format(qa_dir)

    if not os.path.exists(qa_apercal_dir):
        logger.info("Creating directory {0:s}".format(qa_apercal_dir))
        try:
            os.mkdir(qa_apercal_dir)
        except Exception as e:
            logger.error(e)

    original_useful_lines = ["Running prepare ... Done",
                             "Running split ... Done",
                             "Running preflag ... Done",
                             "Running crosscal ... Done",
                             "Running convert ... Done",
                             "Running selfcal and/or continuum and/or polarisation ... Done",
                             "Running line ... Done",
                             "Running transfer ... Done"]

    # go through the list of data directories
    for k in range(len(data_dir_list)):

        # get the log files
        apercal_log_list = glob.glob(
            "{0:s}apercal.log".format(data_dir_list[k]))

        if len(apercal_log_list) != 0:

            # sort log list
            apercal_log_list.sort()

            # go through the log files
            for log_counter in range(len(apercal_log_list)):

                logger.info(
                    "Reading out timing measurement for {0:s}".format(apercal_log_list[log_counter]))

                # to store the results from reading the information
                results = []
                lines_found = []

                # make a copy of useful_lines to use for next log file
                useful_lines = list(original_useful_lines)

                # read logfile
                with open(apercal_log_list[log_counter], "r") as logfile:
                    # go through the lines
                    for logline in logfile:

                        # abort when we are out of useful lines
                        if len(useful_lines) == 0:
                            break

                        # for each line check that a useful line is in there
                        for pos, line in enumerate(useful_lines):
                            # if useful line is found, get value and remove it from list
                            if line in logline:
                                # get the measured time
                                if line == original_useful_lines[-1]:
                                    results.append(logline.split(line)[1])
                                else:
                                    time_in_s = int(logline.rstrip().lstrip().split(line)[
                                        1].split("(")[1].split(")")[0].split("s")[0])
                                    time_str = str(
                                        timedelta(seconds=time_in_s))
                                    results.append(time_str)

                                # the line that was found
                                lines_found.append(line)

                                # remove the useful line that was found
                                useful_lines.remove(line)

                                # move to next logline
                                break

                # take the useful lines found and get only the module
                step_info = np.array([step.split(" ")[1]
                                      for step in lines_found])

                # number of entries in results list
                n_entries = len(results)

                # create a column with file name
                file_name_col = np.array(
                    [os.path.basename(apercal_log_list[log_counter]) for m in range(n_entries)])

                # create table with the above columns
                timing_table = Table([file_name_col, step_info, results], names=(
                    'file_name', 'step', 'time'))

                if log_counter == 0:
                    complete_table = timing_table.copy()
                else:
                    complete_table = vstack([complete_table, timing_table])

            table_output_name = os.path.join(
                qa_apercal_dir, "apercal_log_timeinfo_{0:s}.csv".format(host_name_list[k]))

            try:
                complete_table.write(
                    table_output_name, format="csv", overwrite=True)
            except Exception as e:
                logger.error(e)
        else:
            logger.warning(
                "Could not find any apercal log file in {0:s}".format(data_dir_list[k]))

    # the following is old code for using parselog
    # go through the list of data directories
    # for k in range(len(data_dir_list)):

    #     # get the log files
    #     apercal_log_list = glob.glob(
    #         "{0:s}apercal*.log".format(data_dir_list[k]))

    #     if len(apercal_log_list) != 0:

    #         # sort log list
    #         apercal_log_list.sort()

    #         # go through the log files
    #         for log_counter in range(len(apercal_log_list)):

    #             logger.info(
    #                 "Reading out timing measurement for {0:s}".format(apercal_log_list[log_counter]))

    #             # read timing information
    #             timinginfo = parselog(apercal_log_list[log_counter])

    #             # number of entries
    #             n_entries_in_timinginfo = len(timinginfo)

    #             # create a column with file name
    #             file_name_col = np.array(
    #                 [os.path.basename(apercal_log_list[log_counter]) for m in range(n_entries_in_timinginfo)])

    #             # create a column with beam name
    #             logfile_name = os.path.basename(
    #                 apercal_log_list[log_counter]).split(".log")[0]
    #             if logfile_name == "apercal":
    #                 beam_name_col = np.array([
    #                     "--" for m in range(n_entries_in_timinginfo)])
    #             else:
    #                 beam_name_col = np.array([
    #                     logfile_name.split("apercal")[-1] for m in range(n_entries_in_timinginfo)])

    #             # create table with the above columns
    #             beam_file_table = Table([beam_name_col, file_name_col], names=(
    #                                     'beam', 'file_name'))

    #             # make it an astropy Table
    #             timinginfo_table = Table(
    #                 rows=timinginfo, names=('pipeline_step', 'run_time'))

    #             if log_counter == 0:
    #                 complete_table = hstack(
    #                     [beam_file_table, timinginfo_table])
    #             else:
    #                 tmp_table = hstack([beam_file_table, timinginfo_table])
    #                 complete_table = vstack([complete_table, tmp_table])

    #         table_output_name = "{0:s}apercal_log_timeinfo_{1:s}.csv".format(
    #             qa_apercal_dir, host_name_list[k])

    #         try:
    #             complete_table.write(
    #                 table_output_name, format="csv", overwrite=True)
    #         except Exception as e:
    #             logger.error(e)
    #     else:
    #         logger.warning(
    #             "Could not find any apercal log file in {0:s}".format(data_dir_list[k]))

    logger.info("## Reading apercal timing measurements. Done")

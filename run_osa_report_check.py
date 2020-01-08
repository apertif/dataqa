#!/usr/bin/env python
"""
Script to check which OSA reports exit
    
    ``python run_osa_report_check.py -h``
"""

import os
import time
import numpy as np
import logging
import socket
import glob
import argparse
from astropy.table import Table


def osa_report_check(output_file=''):
    """Function to check the available OSA reports.

    Basic check if the number of OSA reports match the number of checks
    """

    # check that we are running on happili-01
    host_name = socket.gethostname()

    if host_name != "happili-01":
        print("Wrong host. Please use happili-01. Abort")
        raise RuntimeError("Wrong host")

    # data directory
    data_dir = "/data/apertif"

    # the osa report backup path is fixed
    osa_report_path = "/data/apertif/qa/OSA_reports"

    # get a list of existing osa reports
    osa_report_list = glob.glob(os.path.join(osa_report_path, "*.json"))

    # get a list of taskids for which OSA reports exists
    osa_report_taskid = np.array([os.path.basename(report).split("_")[
                                 0] for report in osa_report_list])

    # number of osa reports
    n_reports = len(osa_report_list)

    print("Found {} OSA reports".format(n_reports))

    # get a list of taskids on happili 1
    # avoid getting files before July 10.
    # Not sure if this is the best way to do it
    # use pattern matching
    # already take into account next year
    obs_list_1 = glob.glob(os.path.join(
        data_dir, "1907[1-3][0-9][0-9][0-9][0-9]"))
    obs_list_2 = glob.glob(os.path.join(
        data_dir, "190[8-9][0-3][0-9][0-9][0-9][0-9]"))
    obs_list_3 = glob.glob(os.path.join(
        data_dir, "191[0-2][0-3][0-9][0-9][0-9][0-9]"))
    obs_list_4 = glob.glob(os.path.join(
        data_dir, "20[0-1][0-9][0-3][0-9][0-9][0-9][0-9]"))

    obs_list = np.array([])
    if len(obs_list_1) != 0:
        obs_list = np.append(obs_list, obs_list_1)
    if len(obs_list_2) != 0:
        obs_list = np.append(obs_list, obs_list_2)
    if len(obs_list_3) != 0:
        obs_list = np.append(obs_list, obs_list_3)
    if len(obs_list_4) != 0:
        obs_list = np.append(obs_list, obs_list_4)
    # obs_list = np.append(np.array(obs_list_1), [np.array(obs_list_2),
    #                                             np.array(obs_list_3), np.array(obs_list_4)])

    # number of total taskids on disk
    n_obs = len(obs_list)
    print("Found {} taskids on disk".format(n_obs))

    # get the taskid
    taskid_list = np.array([os.path.basename(taskid)
                            for taskid in obs_list])

    # get the data taskids that are not in the list of report taskids
    # this should give the taskids for which there are no reports
    data_taskid_without_report_list = np.setdiff1d(
        taskid_list, osa_report_taskid)

    # number of taskids without reports
    n_taskids_without_report = len(data_taskid_without_report_list)

    # try to get the OSA from the master list
    osa_master_file = "/home/moss/autocal/csv/ImagingSurveyOSAs-MasterList.csv"

    if os.path.exists(osa_master_file):
        print("Found OSA master file. Getting OSA responsible for a taskid")
        osa_data = Table.read(osa_master_file, format="ascii.csv")
        # convert the start and end dates to the taskid format
        start_date_list = np.array([int("".join(startdate.split("/")[::-1]))
                                    for startdate in osa_data['startdate']])
        end_date_list = np.array([int("".join(enddate.split("/")[::-1]))
                                  for enddate in osa_data['enddate']])
        # now get the osa for a given date
        osa_match_taskid_list = []
        for taskid in data_taskid_without_report_list:
            date_index_list = np.where(
                start_date_list <= int("20"+taskid[:6]))[0]
            if len(date_index_list) == 0:
                osa_match_taskid_list.append("N/A")
            else:
                date_index = date_index_list[-1]
                osa_match_taskid_list.append(osa_data['osa'][date_index])
    else:
        print("Did not find OSA master file. Cannot match taskid to OSA")
        osa_data = None
        osa_match_taskid_list = None

    # print out the taskids:
    print("Found {} taskids without an OSA report. These are:".format(
        n_taskids_without_report))
    for k in range(n_taskids_without_report):
        if osa_match_taskid_list is not None:
            print("\t {0} (OSA: {1})".format(
                data_taskid_without_report_list[k], osa_match_taskid_list[k]))
        else:
            print("\t {0}".format(data_taskid_without_report_list[k]))

    # save to file
    if output_file != '':
        if osa_match_taskid_list is not None:
            output_table = Table(
                [data_taskid_without_report_list, osa_match_taskid_list], names=("taskid", "osa"))
        else:
            output_table = Table(
                [data_taskid_without_report_list], names=("taskid"))

        output_table.write(output_file, format="ascii.csv", overwrite=True)


if __name__ == "__main__":

    print("Checking for which taskids OSA reports exists.")

    print("Warning: This script does not check for incomplete reports")

    parser = argparse.ArgumentParser(
        description='Create overview for QA')

    # only optional argument is the output file
    parser.add_argument("-o", "--output_file", type=str, default='',
                        help='Specify to write the output to a csv file')

    args = parser.parse_args()

    osa_report_check(output_file=args.output_file)

    print("Checking for which taskids OSA reports exists ... Done, but")

    print("Warning: This script does not check for incomplete reports")

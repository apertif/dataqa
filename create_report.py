#!/usr/bin/python2.7

"""
Script to create an html overview

# NOTE:
 In triggered QA crosscal and selfcal plots are distributed over notes.
 Preflag plots are also distributed over the notes.

An option exists to combine the QA from different happilis if run on happili-01

You can specify the name of the target, fluxcal, polcal and OSA which will be saved
in a text file. If this information is available some pages will use it to display
further information.

"""

import os
import sys
from astropy.table import Table
import logging
import glob
import time
import argparse
import socket
from apercal.libs import lib
from report import html_report as hp
from report import html_report_dir as hpd
from report.pipeline_run_time import get_pipeline_run_time
from report.make_nptabel_summary import make_nptabel_csv
from line.cube_stats import combine_cube_stats
from continuum.continuum_tables import merge_continuum_image_properties_table
from cb_plots import make_cb_plots_for_report
from crosscal.dish_delay_plot import get_dish_delay_plots
from scandata import get_default_imagepath


def main():
    start_time = time.time()

    # Create and parse argument list
    # ++++++++++++++++++++++++++++++
    parser = argparse.ArgumentParser(
        description='Create overview for QA')

    # 1st argument: Observation number
    parser.add_argument("obs_id", type=str,
                        help='Observation Number')

    parser.add_argument("--target", type=str, default='',
                        help='Name of the target')

    parser.add_argument("--fluxcal", type=str, default='',
                        help='Name of the flux calibrator')

    parser.add_argument("--polcal", type=str, default='',
                        help='Name of the polarisation calibrator')

    parser.add_argument("--osa", type=str, default='',
                        help='Name of the OSA')

    parser.add_argument("-p", "--path", type=str,
                        help='Path to QA output')

    parser.add_argument("-b", "--basedir", type=str,
                        help='Base directory where the obs id is')

    parser.add_argument("-a", "--add_osa_report", action="store_true", default=False,
                        help='Add only the osa report to the webpage')

    parser.add_argument("-c", "--combine", action="store_true", default=False,
                        help='(Depracated) Set to create a combined report from all happilis on happili-01. It will overwrite the report on happili-01')

    parser.add_argument("--do_not_read_timing", action="store_true", default=False,
                        help='Set to avoid reading timing information. Makes only sense if script is run multiple times or for debugging')

    parser.add_argument("--page_only", action="store_true", default=False,
                        help='Set only create the webpages themselves')

    # this mode will make the script look only for the beams processed by Apercal on a given node
    parser.add_argument("--trigger_mode", action="store_true", default=False,
                        help='Set it to run Autocal triggering mode automatically after Apercal.')

    args = parser.parse_args()

    obs_id = args.obs_id
    qa_dir = args.path
    base_dir = args.basedir
    do_combine = args.combine
    add_osa_report = args.add_osa_report

    # directory where the output will be of pybdsf will be stored
    if qa_dir is None:
        if base_dir is not None:
            qa_dir = get_default_imagepath(obs_id, basedir=base_dir)
        else:
            qa_dir = get_default_imagepath(obs_id)

        # check that path exists
        if not os.path.exists(qa_dir):
            print(
                "Directory {0:s} does not exist and will be created".format(qa_dir))
            os.makedirs(qa_dir)

    # check the mode to run the validation
    qa_report_dir = "{0:s}report".format(
        qa_dir)

    # check that this directory exists (just in case)
    if not os.path.exists(qa_report_dir):
        print("Directory {0:s} does not exist and will be created".format(
            qa_report_dir))
        os.makedirs(qa_report_dir)

    lib.setup_logger(
        'debug', logfile='{0:s}/create_report.log'.format(qa_report_dir))
    logger = logging.getLogger(__name__)

    # if osa report should be added, check it is available
    if add_osa_report:
        # name of the osa report for this observation
        osa_report = os.path.join(
            qa_report_dir, "OSA_Report/{}_OSA_report.ecsv".format(obs_id))

        # check that the file is actually there
        if not os.path.exists(osa_report):
            logger.error("No OSA report found. Abort")
            return -1
    else:
        osa_report = ''

    # Saving observation information if they do not exist yet
    # =======================================================

    table_name = "{0}_obs.ecsv".format(obs_id)

    table_name_with_path = os.path.join(qa_dir, table_name)

    if not os.path.exists(table_name_with_path):

        obs_info = Table([
            [obs_id],
            [args.target],
            [args.fluxcal],
            [],
            [args.polcal],
            [],
            [args.osa]], names=(
            'Obs_ID', 'Target', 'Flux_Calibrator', 'Flux_Calibrator_Obs_IDs', 'Pol_Calibrator', 'Pol_Calibrator_Obs_IDs', 'OSA'))

        try:
            obs_info.write(
                table_name_with_path, format='ascii.ecsv', overwrite=True)
        except Exception as e:
            logger.warning("Saving observation information in {0} failed.".format(
                table_name_with_path))
            logger.exception(e)
        else:
            logger.info(
                ("Saving observation information in {0} ... Done.".format(table_name_with_path)))
    else:
        logger.info(
            ("Observation information already exists. Reading {0}.".format(table_name_with_path)))
        obs_info = Table.read(table_name_with_path, format="ascii.ecsv")

    # check on which happili we are:
    host_name = socket.gethostname()

    if args.trigger_mode:
        logger.info(
            "--> Running report QA in trigger mode. Looking only for data processed by Apercal on {0:s} <--".format(host_name))
    elif do_combine:
        logger.info("Combining QAs from different happilis")
        if host_name != "happili-01":
            logger.warning("You are not working on happili-01.")
            logger.warning("Cannot combine QA from different happilis")
            do_combine = False
    elif host_name != "happili-01" and not args.trigger_mode:
        logger.warning("You are not working on happili-01.")
        logger.warning("The script will not process all beams")
        logger.warning("Please switch to happili-01")

    apercal_log_file = "/data/apertif/{0:s}/apercal.log".format(
        obs_id)

    # logging.basicConfig(filename='{0:s}/create_report.log'.format(qa_dir), level=logging.DEBUG,
    #                     format='%(asctime)s - %(levelname)s: %(message)s')

    # getting timing measurment for apercal only in trigger mode
    # if not add_osa_report and not args.do_not_read_timing:
    if args.trigger_mode:
        try:
            get_pipeline_run_time(obs_id, trigger_mode=args.trigger_mode)
        except Exception as e:
            logger.error(e)

    # the subpages to be created
    subpages = ['observing_log', 'summary',  'beamweights', 'inspection_plots', 'preflag', 'crosscal',
                'selfcal', 'continuum', 'polarisation', 'line', 'mosaic', 'apercal_log']

    logger.info("#### Create report directory structure")

    # copy the js and css files
    js_file_name = "{0:s}/report_fct.js".format(
        hp.__file__.split("/html_report.py")[0])
    css_file_name = "{0:s}/report_style.css".format(
        hp.__file__.split("/html_report.py")[0])

    # for copying osa_files:
    osa_nb_file = "{0:s}/OSA_report.ipynb".format(
        hp.__file__.split("/html_report.py")[0])
    osa_py_file = "{0:s}/osa_functions.py".format(
        hp.__file__.split("/html_report.py")[0])

    osa_files = [osa_nb_file, osa_py_file]

    # Check that directory of the qa exists
    if not os.path.exists(qa_dir):
        logger.error(
            "Directory {0:s} does not exists. Abort".format(qa_report_dir))
        return -1
    else:
        # do things that should only happen on happili-01 when the OSA runs this function
        if not args.trigger_mode and host_name == "happili-01" and not args.page_only:
            # go through some of the subpages and process numpy files
            for page in subpages:
                # exclude non-apercal modules (and mosaic)
                if page != "apercal_log" or page != "inspection_plots" or page != "summary" or page != "mosaic":
                    # just run it on preflag for now
                    if page == "preflag" or page == "crosscal" or page == "convert" or page == "selfcal" or page == "continuum":
                        try:
                            logger.info(
                                "## Getting summary table for {}".format(page))
                            make_nptabel_csv(
                                obs_id, page, output_path=os.path.join(qa_dir, page))
                        except Exception as e:
                            logger.warning(
                                "## Getting summary table for {} failed".format(page))
                            logger.exception(e)
                        else:
                            logger.info(
                                "## Getting summary table for {} ... Done".format(page))

                # merge the continuum image properties
                if page == 'continuum':
                    merge_continuum_image_properties_table(obs_id, qa_dir)

                # get line statistics
                if page == 'line':
                    combine_cube_stats(obs_id, qa_dir)

            # create dish delay plot
            try:
                logger.info("Getting dish delay plot")
                get_dish_delay_plots(obs_id, obs_info['Flux_Calibrator'][0])
            except Exception as e:
                logger.warning("Getting dish delay plot ... Failed")
                logger.exception(e)
            else:
                logger.info("Getting dish delay plot ... Done")

            # create compound beam plots
            try:
                logger.info("Getting compound beam plots")
                make_cb_plots_for_report(obs_id, qa_dir)
            except Exception as e:
                logger.warning("Getting compound beam plots ... Failed")
                logger.exception(e)
            else:
                logger.info("Getting compound beam plots ... Done")

    # Create directory structure for the report
    if not add_osa_report:
        logger.info("#### Creating directory structrure")
        try:
            hpd.create_report_dirs(
                obs_id, qa_dir, subpages, css_file=css_file_name, js_file=js_file_name, trigger_mode=args.trigger_mode, do_combine=do_combine, obs_info=obs_info, osa_files=osa_files)
        except Exception as e:
            logger.error(e)
        else:
            logger.info("#### Creating directory structrure ... Done")

    logger.info("#### Creating report")

    try:
        hp.create_main_html(qa_report_dir, obs_id, subpages,
                            css_file=css_file_name, js_file=js_file_name, obs_info=obs_info, osa_report=osa_report)
    except Exception as e:
        logger.error(e)

    logger.info("#### Report. Done ({0:.0f}s)".format(
        time.time()-start_time))


if __name__ == "__main__":
    main()

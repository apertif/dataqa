"""
This script contains functionality to run all QA automatically after being triggered at the end of apercal
"""

import os
import time
import numpy as np
import logging
import socket
from apercal.libs import lib
from apercal.subs import calmodels as subs_calmodels
from astropy.table import Table

from dataqa.scandata import get_default_imagepath


def run_triggered_qa(targets, fluxcals, polcals, steps=None, basedir=None, osa=''):
    """Function to run all QA steps.

    Function is called as
    return_msg = run_triggered_qa(
        tdict['target'], tdict['cal1'], tdict['cal2'])

    With the first three variables defined (the same way as autocal) as
        targets = (190505048, 'LH_WSRT', array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))

        fluxcals = [(190505017, '3C147_9', 9), (190505016, '3C147_8', 8), (190505015, '3C147_7', 7), (190505014, '3C147_6', 6), (190505013, '3C147_5', 5),
                     (190505012, '3C147_4', 4), (190505011, '3C147_3', 3), (190505010, '3C147_2', 2), (190505009, '3C147_1', 1), (190505008, '3C147_0', 0)]

        polcals = [(190506001, '3C286_0', 0), (190506002, '3C286_1', 1), (190506003, '3C286_2', 2), (190506004, '3C286_3', 3), (190506005, '3C286_4', 4),
                    (190506006, '3C286_5', 5), (190506007, '3C286_6', 6), (190506008, '3C286_7', 7), (190506009, '3C286_8', 8), (190506010, '3C286_9', 9)]

    If steps is not provided then all steps except mosaic will be performed:
        steps = ['preflag', 'crosscal', 'selfcal',
                 'continuum', 'line', 'mosaic', 'report']
    For all steps including mosaic:
        steps = ['preflag', 'crosscal', 'selfcal',
                 'continuum', 'line', 'mosaic', 'report']
    It is possible to select a certain step:
        steps = ['mosaic']

    test call can look like this: 
        from dataqa.run_qa import run_triggered_qa
        run_triggered_qa((190505048, 'LH_WSRT', [0]), [(190505048, '3C147_10', 10)], [(190505048, '3C286_10', 10)], steps=['report'])
    """

    # for time measurement
    start_time = time.time()

    # Process input parameters
    # (same as in start_apercal_pipeline)
    # ========================

    (taskid_target, name_target, beamlist_target) = targets

    if fluxcals:
        name_fluxcal = str(fluxcals[0][1]).strip().split('_')[0].upper()
    else:
        name_fluxcal = ''
    if polcals:
        name_polcal = str(polcals[0][1]).strip().split('_')[0].upper()
    else:
        name_polcal = ''

    if steps is None:
        # steps = ['preflag', 'crosscal', 'selfcal',
        #          'continuum', 'line', 'mosaic', 'report']
        steps = ['inspection_plots', 'preflag', 'crosscal', 'selfcal',
                 'continuum', 'line', 'report']

    # Set up
    # ======

    # Get host name
    host_name = socket.gethostname()

    # QA directory
    if basedir is not None:
        qa_dir = get_default_imagepath(taskid_target, basedir=basedir)
    else:
        qa_dir = get_default_imagepath(taskid_target)

    # check that path exists
    if not os.path.exists(qa_dir):
        print(
            "Directory {0:s} does not exist and will be created".format(qa_dir))
        try:
            os.mkdir(qa_dir)
        except Exception as e:
            print(e)

    # start log file
    # logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
    #                     filename='{0:s}{1:s}_triggered_qa.log'.format(qa_dir, host_name), level=logging.DEBUG)

    lib.setup_logger(
        'debug', logfile='{0:s}{1:s}_triggered_qa.log'.format(qa_dir, host_name))
    logger = logging.getLogger(__name__)

    logger.info("#######################")
    logger.info("Input parameters:")
    logger.info("target={0:s}".format(str(targets)))
    logger.info("fluxcals={0:s}".format(str(fluxcals)))
    logger.info("polcals={0:s}".format(str(polcals)))
    logger.info("#######################")

    logger.info('#######################')
    logger.info('#### Running all QA steps on {0:s}'.format(host_name))
    logger.info('#######################')

    # If both fluxcal and polcal polarized, remove polcal
    # (taken from start_pipeline)
    if subs_calmodels.is_polarised(name_polcal) and subs_calmodels.is_polarised(name_fluxcal):
        name_polcal = ""

    if (fluxcals and fluxcals != '') and (polcals and polcals != ''):
        assert(len(fluxcals) == len(polcals))

    # Exchange polcal and fluxcal if specified in the wrong order
    # (taken from start_pipeline)
    # (except for how the names are switched)
    if not subs_calmodels.is_polarised(name_polcal) and name_polcal != '':
        if subs_calmodels.is_polarised(name_fluxcal):
            logger.debug("Switching polcal and fluxcal because " + name_polcal +
                         " is not polarised")
            fluxcals, polcals = polcals, fluxcals
            name_fluxcal, name_polcal = name_polcal, name_fluxcal
            #name_polcal = str(polcals[0][1]).strip()
        else:
            logger.debug("Setting polcal to '' since " +
                         name_polcal + " is not polarised")
            name_polcal = ""
    elif name_polcal != '':
        logger.debug("Polcal " + name_polcal + " is polarised, all good")

    logger.info("## Observation of target: {0:s}, flux calibrator: {1:s}, polarisation calibrator: {2:s}".format(
        name_target, name_fluxcal, name_polcal))

    # Write information about the observation into a txt file for later
    # This information is important for the OSA report
    # =================================================================

    summary_table = Table([
        [taskid_target],
        [name_target],
        [name_fluxcal],
        [name_polcal],
        [osa]], names=(
        'Obs_ID', 'Target', 'Flux_Calibrator', 'Pol_Calibrator', 'OSA'))

    table_name = "{0}_obs.ecsv".format(taskid_target)

    table_name_with_path = os.path.join(qa_dir, table_name)

    try:
        summary_table.write(
            table_name_with_path, format='ascii.ecsv', overwrite=True)
    except Exception as e:
        logger.warning("Saving observation information in {0} failed.".format(
            table_name_with_path))
        logger.exception(e)
    else:
        logger.info(
            ("Saving observation information in {0} ... Done.".format(table_name_with_path)))

    # Inspection Plots
    # ================

    if 'inspection_plots' in steps and host_name == 'happili-01':

        start_time_inspection_plot = time.time()

        # get inspection plots for target
        logger.info("#### Inspection plot QA for {}...".format(name_target))

        try:
            inspection_plot_msg = os.system(
                'python /home/schulz/apercal/dataqa/run_inspection_plot.py {0:d} {1:s}'.format(taskid_target, name_target))
            logger.info(
                "Getting inspection plots finished with msg {0}".format(inspection_plot_msg))
            logger.info(
                "#### Inspection plot QA {0}... Done ".format(name_target))
        except Exception as e:
            logger.warning(
                "Inspection plot QA for {} failed. Continue with next QA".format(name_target))
            logger.exception(e)

        # get inspection plot for flux calibrator
        logger.info("#### Inspection plot QA for {}...".format(name_fluxcal))

        for (taskid_cal, name_cal, beamnr_cal) in fluxcals:

            try:
                inspection_plot_msg = os.system(
                    'python /home/schulz/apercal/dataqa/run_inspection_plot.py {0:d} {1:s} -c --beam={2:d} --cal_id={3:d}'.format(taskid_target, name_fluxcal, beamnr_cal, taskid_cal))
                logger.info(
                    "Getting inspection plots finished with msg {0}".format(inspection_plot_msg))
                logger.info("#### Inspection plot QA for {0} beam {1} ... Done".format(
                    name_fluxcal, beamnr_cal))
            except Exception as e:
                logger.warning(
                    "Inspection plot QA for {} beam {1} failed. Continue with next QA".format(name_fluxcal, beamnr_cal))
                logger.exception(e)

        # get inspection plot for pol calibrator if it exists
        if name_polcal != '':
            logger.info(
                "#### Inspection plot QA for {}...".format(name_polcal))

            for (taskid_cal, name_cal, beamnr_cal) in polcals:

                try:
                    inspection_plot_msg = os.system(
                        'python /home/schulz/apercal/dataqa/run_inspection_plot.py {0:d} {1:s} -c --beam={2:d} --cal_id={3:d}'.format(taskid_target, name_fluxcal, beamnr_cal, taskid_cal))
                    logger.info(
                        "Getting inspection plots finished with msg {0}".format(inspection_plot_msg))
                    logger.info("#### Inspection plot QA for {0} beam {1} ... Done".format(
                        name_polcal, beamnr_cal))
                except Exception as e:
                    logger.warning(
                        "Inspection plot QA for {} beam {1} failed. Continue with next QA".format(name_polcal, beamnr_cal))
                    logger.exception(e)

        logger.info("#### Inspection plot QA ... Done (time {0:.1f}s)".format(
            time.time()-start_time_inspection_plot))
    else:
        logger.warning("#### Did not perform inspection plot QA")

    # Preflag QA
    # ==========

    if 'preflag' in steps and name_fluxcal != '':

        logger.info("#### Running preflag QA ...")

        start_time_preflag = time.time()

        try:
            preflag_msg = os.system(
                'python /home/apercal/dataqa/run_rfinder.py {0:d} {1:s} --trigger_mode'.format(taskid_target, name_fluxcal))
            logger.info(
                "Preflag QA finished with msg {0}".format(preflag_msg))
            logger.info("#### Running preflag QA ... Done (time {0:.1f}s)".format(
                time.time()-start_time_preflag))
        except Exception as e:
            logger.warning("Preflag QA failed. Continue with next QA")
            logger.exception(e)
    else:
        logger.warning("#### Did not perform preflag QA")

    # Crosscal QA
    # ===========

    if 'crosscal' in steps and name_fluxcal != '' and name_polcal != '':

        logger.info('#### Running crosscal QA ...')

        start_time_crosscal = time.time()

        try:
            crosscal_msg = os.system(
                'python /home/apercal/dataqa/run_ccal_plots.py {0:d} {1:s} {2:s} --trigger_mode'.format(taskid_target, name_fluxcal, name_polcal))
            logger.info(
                "Crosscal QA finished with msg {0}".format(crosscal_msg))
            logger.info("#### Running crosscal QA ... Done (time {0:.1f}s)".format(
                time.time()-start_time_crosscal))
        except Exception as e:
            logger.warning("Crosscal QA failed. Continue with next QA")
            logger.exception(e)
    else:
        logger.warning("#### Did not perform crosscal QA")

    # Selfcal QA
    # ==========

    if 'selfcal' in steps:

        logger.info('#### Running selfcal QA ...')

        start_time_selfcal = time.time()

        try:
            selfcal_msg = os.system(
                'python /home/apercal/dataqa/run_scal_plots.py {0:d} {1:s} --trigger_mode'.format(taskid_target, name_target))
            logger.info(
                "Selfcal QA finished with msg {0}".format(selfcal_msg))
            logger.info("#### Running selfcal QA ... Done (time {0:.1f}s)".format(
                time.time()-start_time_selfcal))
        except Exception as e:
            logger.warning("Selfcal QA failed. Continue with next QA")
            logger.exception(e)
    else:
        logger.warning("#### Did not perform selfcal QA")

    # Mosaic QA
    # ==========

    if 'mosaic' in steps and host_name == 'happili-01':

        logger.info('#### Running mosaic QA ...')

        start_time_mosaic = time.time()

        try:
            # Create the mosaic
            logger.info('## Making the mosaic ...')
            start_time_make_mosaic = time.time()
            make_mosaic_msg = os.system(
                'python /home/apercal/dataqa/make_mosaic_image.py {0:d}'.format(taskid_target))
            logger.info(
                "Making mosaic finished with msg {0}".format(make_mosaic_msg))
            logger.info("## Making the mosaic ... Done (time {0:.1f}s)".format(
                time.time()-start_time_make_mosaic))

            # Run the validation tool
            logger.info('## Run validation ...')
            start_time_mosaic_validation = time.time()
            mosaic_validation_msg = os.system(
                'python /home/apercal/dataqa/run_continuum_validation.py {0:d} --for_mosaic'.format(taskid_target))
            logger.info(
                "Mosaic validation finished with msg {0}".format(mosaic_validation_msg))
            logger.info("## Run validation ... Done (time {0:.1f}s)".format(
                time.time()-start_time_mosaic_validation))

            logger.info("#### Running mosaic QA ... Done (time {0:.1f}s)".format(
                time.time()-start_time_mosaic))
        except Exception as e:
            logger.warning("Mosaic QA failed. Continue with next QA")
            logger.exception(e)
    else:
        logger.warning("#### Did not perform mosaic QA")

    # Line QA
    # =======

    if 'line' in steps:

        logger.info('#### Running line QA ...')

        start_time_line = time.time()

        try:
            # Get cube statistic without continuum subtraction
            logger.info(
                '## Get cube statistic prior to continuum subtraction ...')
            start_time_get_cube_stat = time.time()
            cube_stat_msg = os.system(
                'python /home/apercal/dataqa/run_cube_stats.py {0:d} --trigger_mode'.format(taskid_target))
            logger.info(
                "Cube stat finished with msg {0}".format(cube_stat_msg))
            logger.info("## Get cube statistic prior to continuum subtraction ... Done (time {0:.1f}s)".format(
                time.time()-start_time_get_cube_stat))

            # Subtract continuum
            logger.info('## Subtract continuum ...')
            start_time_subtract_continuum = time.time()
            subtract_cont_msg = os.system(
                'python /home/apercal/dataqa/subtract_continuum.py {0:d} --trigger_mode'.format(taskid_target))
            logger.info(
                "Continuum subtraction finished with msg {0}".format(subtract_cont_msg))
            logger.info("## Subtract continuum ... Done (time {0:.1f}s)".format(
                time.time()-start_time_subtract_continuum))

            # Get cube statistic after continuum subtraction
            logger.info(
                '## Get cube statistic after continuum subtraction ...')
            start_time_get_cube_stat_cont = time.time()
            get_cube_stat_cont_msg = os.system(
                'python /home/apercal/dataqa/run_cube_stats_cont.py {0:d} --trigger_mode'.format(taskid_target))
            logger.info(
                "Cube stat cont finished with msg {0}".format(get_cube_stat_cont_msg))
            logger.info("## Get cube statistic after continuum subtraction ... Done (time {0:.1f}s)".format(
                time.time()-start_time_get_cube_stat_cont))

            logger.info("#### Running line QA ... Done (time {0:.1f}s)".format(
                time.time()-start_time_line))
        except Exception as e:
            logger.warning("Line QA failed. Continue with next QA")
            logger.exception(e)
    else:
        logger.warning("#### Did not perform line QA")

    # Continuum QA
    # ============

    if 'continuum' in steps:

        logger.info('#### Running continuum QA ...')

        start_time_continuum = time.time()

        try:
            continuum_msg = os.system(
                'python /home/apercal/dataqa/run_continuum_validation.py {0:d} --trigger_mode'.format(taskid_target))
            logger.info(
                "Continuum QA finished with msg {0}".format(continuum_msg))
            logger.info("#### Running continuum QA ... Done (time {0:.1f}s)".format(
                time.time()-start_time_continuum))
        except Exception as e:
            logger.warning("Continuum QA failed. Continue with next QA")
            logger.exception(e)
    else:
        logger.warning("#### Did not perform continuum QA")

    # Create report
    # =============

    if 'report' in steps:

        logger.info('#### Create report ...')

        start_time_report = time.time()

        try:
            report_msg = os.system(
                'python /home/apercal/dataqa/create_report.py {0:d} --trigger_mode'.format(taskid_target))
            logger.info(
                "Report finished with msg {0}".format(report_msg))
            logger.info("#### Create report ... Done (time {0:.1f}s)".format(
                time.time()-start_time_report))
        except Exception as e:
            logger.warning("Creating report failed.")
            logger.exception(e)
    else:
        logger.warning("#### Did not create a report")

    # Finish
    # ======
    logger.info('#######################')
    logger.info(
        '#### Running all QA steps on {0:s} ... Done (time {1:.1f}s)'.format(host_name, time.time()-start_time))
    logger.info('#######################')

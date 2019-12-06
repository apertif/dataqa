"""
Script to automatically run crosscal plots
Requires a scan number
Optionally takes a directory for writing plots
"""

import os
from selfcal import selfcal_plots as scplots
import argparse
from timeit import default_timer as timer
from scandata import get_default_imagepath
from selfcal.selfcal_maps import get_selfcal_maps
import time
from apercal.libs import lib
import logging

start = timer()

parser = argparse.ArgumentParser(description='Generate selfcal QA plots')

# 1st argument: File name
parser.add_argument("scan", help='Scan of target field')
parser.add_argument("target", help='Target name')

parser.add_argument('-p', '--path', default=None,
                    help='Destination for images')

parser.add_argument('-b', '--basedir', default=None,
                    help='Data directory')

parser.add_argument('-M', '--maps', default=True,
                    action='store_false', help='Do not generate selfcal maps')
parser.add_argument('-P', '--phase', default=True,
                    action='store_false', help='Do not generate phase plots')
parser.add_argument('-A', '--amplitude', default=True,
                    action='store_false', help='Do not generate amplitude plots')

# this mode will make the script look only for the beams processed by Apercal on a given node
parser.add_argument("--trigger_mode", action="store_true", default=False,
                    help='Set it to run Autocal triggering mode automatically after Apercal.')

args = parser.parse_args()

# If no path is given change to default QA path
if args.path is None:
    output_path = get_default_imagepath(args.scan, basedir=args.basedir)

    # check that selfcal qa directory exists
    output_path = os.path.join(output_path, "selfcal/")

    if not os.path.exists(output_path):
        os.mkdir(output_path)
else:
    output_path = args.path

# Create log file
lib.setup_logger(
    'info', logfile='{0:s}run_scal_plots.log'.format(output_path))
logger = logging.getLogger(__name__)

# Get selfcal maps
if args.maps:
    try:
        logger.info("#### Creating selfcal maps ...")
        start_time_maps = time.time()
        get_selfcal_maps(args.scan, output_path,
                         trigger_mode=args.trigger_mode)
        logger.info("#### Creating selfcal maps. Done ({0:.0f}s)".format(
            time.time()-start_time_maps))
    except Exception as e:
        logger.error(e)
        logger.error("#### Creating selfcal maps failed")
else:
    logger.info("#### Not generating selfcal maps")

# Get phase plots
if args.phase:
    try:
        logger.info("#### Creating phase plots")
        start_time_plots = time.time()
        PH = scplots.PHSols(args.scan, args.target,
                            trigger_mode=args.trigger_mode, basedir=args.basedir)
        PH.get_data()
        PH.plot_phase(imagepath=output_path)
        logger.info('#### Done with phase plots ({0:.0f}s)'.format(
            time.time()-start_time_plots))
    except Exception as e:
        logger.error(e)
        logger.error("Creating phase plots failed.")
else:
    logger.info("#### Not generating phase plots")

# Get amplitude plots
if args.amplitude:
    try:
        logger.info("#### Creating amplitude plots")
        start_time_plots = time.time()
        AMP = scplots.AMPSols(args.scan, args.target,
                              trigger_mode=args.trigger_mode, basedir=args.basedir)
        AMP.get_data()
        AMP.plot_amp(imagepath=output_path)
        logger.info('#### Done with amplitude plots ({0:.0f}s)'.format(
            time.time()-start_time_plots))
    except Exception as e:
        logger.error(e)
        logger.error("Creating amplitude plots failed.")
else:
    logger.info("#### Not generating amplitude plots")


end = timer()
print 'Elapsed time to generate self-calibration data QA inpection plots and images is {} minutes'.format((end - start)/60.)

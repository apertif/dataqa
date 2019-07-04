"""
Script to automatically run preflag qa

Combines the preflag plots

Requires a scan number
Optionally takes a directory for writing plots
"""

import os
from selfcal import selfcal_plots as scplots
import argparse
from timeit import default_timer as timer
from scandata import get_default_imagepath
from preflag import preflag_plots
import time
from apercal.libs import lib
import logging

start = timer()

parser = argparse.ArgumentParser(description='Combine preflag QA plots')

# 1st argument: File name
parser.add_argument("scan", help='Scan of target field')

# path options
parser.add_argument('-p', '--path', default=None,
                    help='Destination for images')
parser.add_argument('-b', '--basedir', default=None,
                    help='Directory where scan is located')

# this mode will make the script look only for the beams processed by Apercal on a given node
parser.add_argument("--trigger_mode", action="store_true", default=False,
                    help='Set it to run Autocal triggering mode automatically after Apercal.')

args = parser.parse_args()

# If no path is given change to default QA path
if args.path is None:
    if args.basedir is not None:
        qa_dir = get_default_imagepath(args.scan, basedir=args.basedir)
    else:
        qa_dir = get_default_imagepath(args.scan)

    # check that selfcal qa directory exists
    qa_preflag_dir = os.path.join(qa_dir, "preflag")

    if not os.path.exists(qa_preflag_dir):
        os.mkdir(qa_preflag_dir)
else:
    qa_preflag_dir = args.path

# Create log file
lib.setup_logger(
    'info', logfile=os.path.join(qa_preflag_dir, 'run_preflag_qa.log'))
logger = logging.getLogger(__name__)

logger.info("Running preflag QA")

# now combine the plots
try:
    start_time = time.time()
    preflag_plots.combine_preflag_plots(
        qa_preflag_dir, trigger_mode=args.trigger_mode)
except Exception as e:
    logger.warning("Running preflag QA failed")
    logger.exception(e)
else:
    logger.warning("Running preflag QA ... Done ({0:.0f}s)".format(
        time.time()-start_time))

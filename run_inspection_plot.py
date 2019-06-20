"""
Script to automatically retrieve inspection plots from ALTA
for the QA
Requires a scan number
Optionally takes a directory for writing plots
"""

import os
import socket
import argparse
from timeit import default_timer as timer
from scandata import get_default_imagepath
from inspection_plots.inspection_plots import get_inspection_plots
import time
from apercal.libs import lib
import logging

start = timer()

parser = argparse.ArgumentParser(description='Generate selfcal QA plots')

# 1st argument: File name
parser.add_argument("obs_id", help='ID of observation of target field')

parser.add_argument('-p', '--path', default=None,
                    help='Destination for images')
parser.add_argument('-b', '--basedir', default=None,
                    help='Directory of obs id')

# this mode will make the script look only for the beams processed by Apercal on a given node
# parser.add_argument("--trigger_mode", action="store_true", default=False,
#                     help='Set it to run Autocal triggering mode automatically after Apercal.')

args = parser.parse_args()

# If no path is given change to default QA path
if args.path is None:
    if args.basedir is not None:
        output_path = get_default_imagepath(args.obs_id, basedir=args.basedir)
    else:
        output_path = get_default_imagepath(args.obs_id)

    # check that selfcal qa directory exists
    qa_plot_dir = os.path.join(output_path, "inspection_plots")

    if not os.path.exists(qa_plot_dir):
        os.mkdir(qa_plot_dir)
else:
    qa_plot_dir = args.path

# Create log file
lib.setup_logger(
    'info', logfile=os.path.join(qa_plot_dir, 'get_inspection_plot.log'))
logger = logging.getLogger(__name__)

# Run function to get plots
try:
    logger.info("#### Getting inspection plots ...")
    start_time_plots = time.time()
    get_inspection_plots(args.obs_id, qa_plot_dir)
except Exception as e:
    logger.error(e)
    logger.error("#### Getting inspection plots failed")
else:
    logger.info("#### Getting inspection plots... Done ({0:.0f}s)".format(
        time.time()-start_time_plots))

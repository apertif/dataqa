#!/usr/bin/env python
"""
Script to automatically run RFInder on flux calibrator
Requires a taskID and name of flux calibrator
"""

import os
import argparse
from timeit import default_timer as timer
import logging
from apercal.libs import lib
from dataqa.scandata import get_default_imagepath
import socket
import glob

start = timer()

parser = argparse.ArgumentParser(description='Run RFInder')

# 1st argument: taskID
parser.add_argument("taskID", help='Task ID of target field')

# 2nd argument: fluxcal name
parser.add_argument("fluxcal", help='Fluxcal name')

# 3rd argument: destination for images, optional
parser.add_argument('-p', '--path', default=None,
                    help='Destination for images')

parser.add_argument('-b', '--basedir', default=None,
                    help='Data directory')

# this mode will make the script look only for the beams processed by Apercal on a given node
parser.add_argument("--trigger_mode", action="store_true", default=False,
                    help='Set it to run Autocal triggering mode automatically after Apercal')

args = parser.parse_args()

# If no path is given change to default QA path
if args.path is None:
    output_path = get_default_imagepath(args.taskID, basedir=args.basedir)

    # check that preflag qa directory exists
    output_path = "{0:s}preflag/".format(output_path)

    if not os.path.exists(output_path):
        os.mkdir(output_path)
else:
    output_path = args.path

# Create logging file
lib.setup_logger(
    'debug', logfile='{0:s}run_rfinder.log'.format(output_path))
logger = logging.getLogger(__name__)

# get data directories depending on the host name
host_name = socket.gethostname()
if args.trigger_mode:
    logger.info(
        "--> Running line QA in trigger mode. Looking only for data processed by Apercal on {0:s} <--".format(host_name))
    data_beam_dir_list = glob.glob(
        "/data/apertif/{}/[0-3][0-9]".format(args.taskID))
elif host_name != "happili-01" and not args.trigger_mode:
    logger.warning("You are not working on happili-01.")
    logger.warning("The script will not process all beams")
    logger.warning("Please switch to happili-01")
    data_beam_dir_list = glob.glob(
        "/data/apertif/{}/[0-3][0-9]".format(args.taskID))
else:
    logger.info("Running on happili-01. Using data from all nodes.")
    data_beam_dir_list = glob.glob(
        "/data*/apertif/{}/[0-3][0-9]".format(args.taskID))

# Run RFInder
# iterate over beams
for beam_dir in data_beam_dir_list:

    # get beam
    b = beam_dir.split("/")[-1]

    # get qa path and name MS file
    qapath = "{0:s}{1:s}/".format(output_path, b)
    msfile = '{0:s}.MS'.format(args.fluxcal)

    # create beam directory for QA if necessary
    if not os.path.exists(qapath):
        os.mkdir(qapath)

    datapath = '{0:s}/raw/'.format(beam_dir)

    # if b < 10:
    #     datapath='/data/apertif/{0:s}/{1:02d}/raw/'.format(args.taskID, b)
    # if 10 <= b < 20:
    #     datapath='/data2/apertif/{0:s}/{1:02d}/raw/'.format(args.taskID, b)
    # if 20 <= b < 30:
    #     datapath='/data3/apertif/{0:s}/{1:02d}/raw/'.format(args.taskID, b)
    # if 30 <= b < 40:
    #     datapath='/data4/apertif/{0:s}/{1:02d}/raw/'.format(args.taskID, b)
    rfinder_command = ("python /home/apercal/pipeline/bin/rfinder -idir {0:s} -i {1:s} -tel apertif "
                       "-mode use_flags -odir {2:s} -fl 0 -tStep 5 -yesClp").format(datapath, msfile, qapath)
    # print rfinder_command
    try:
        logging.info("Running RFinder for beam {0:s}".format(b))
        os.system(rfinder_command)
        logging.info("Running RFinder for beam {0:s} ... Done".format(b))
    except Exception as e:
        logger.error(e)
        logging.error("Running RFinder for beam {0:s} failed".format(b))

    # move 2D plot to where report can find it (quick & dirty hack)
    old2d = "{0:s}/rfi_q/plots/movies/Time_2Dplot_movie.gif".format(qapath)
    new2d = "{0:s}/Time_2D_{1:s}.png".format(qapath, args.fluxcal)
    oldaa = "{0:s}/rfi_q/plots/movies/AltAz_movie.gif".format(qapath)
    newaa = "{0:s}/test_AltAz_{1:s}.png".format(qapath, args.fluxcal)
    try:
        os.rename(old2d, new2d)
    except:
        pass
    try:
        os.rename(oldaa, newaa)
    except:
        pass

end = timer()
logger.info('Elapsed time to run RFinder is {} minutes'.format(
    (end-start)/60.))

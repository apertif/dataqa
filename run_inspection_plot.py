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


def main():
    start = timer()

    parser = argparse.ArgumentParser(description='Generate selfcal QA plots')

    # 1st argument: File name
    parser.add_argument("obs_id", help='ID of observation of target field')

    parser.add_argument(
        "src_name", help='Name of the calibrator or target of the plots')

    parser.add_argument("-c", "--calibrator", action="store_true", default=False,
                        help='Set if a calibrator is used. Also requires beam and cal_id')

    parser.add_argument("--beam", type=int, default=None,
                        help='If src_name is a calibrator set the beam number')

    parser.add_argument("--cal_id", default=None,
                        help='Obs ID of the calibrator')

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
            output_path = get_default_imagepath(
                args.obs_id, basedir=args.basedir)
        else:
            output_path = get_default_imagepath(args.obs_id)

        # check that selfcal qa directory exists
        qa_plot_dir = os.path.join(output_path, "inspection_plots")

        if not os.path.exists(qa_plot_dir):
            os.mkdir(qa_plot_dir)
    else:
        qa_plot_dir = args.path

    # create a directory with the src_name to put
    if args.src_name is not None:
        qa_plot_dir = os.path.join(qa_plot_dir, args.src_name)

        if not os.path.exists(qa_plot_dir):
            os.mkdir(qa_plot_dir)

    # if it is a calibrator then put the plots into a beam directory
    if args.calibrator:
        if args.beam is None:
            print("ERROR: Please specify beam of calibrator")
        elif args.cal_id is None:
            print("ERROR: Please specify id of calibrator")
        else:
            is_calibrator = True

            qa_plot_dir = os.path.join(qa_plot_dir, args.beam)

            if not os.path.exists(qa_plot_dir):
                os.mkdir(qa_plot_dir)
    else:
        is_calibrator = False

    # Create log file
    lib.setup_logger(
        'info', logfile=os.path.join(qa_plot_dir, 'get_inspection_plot.log'))
    logger = logging.getLogger(__name__)

    # Run function to get plots
    try:
        logger.info("#### Getting inspection plots ...")
        start_time_plots = time.time()
        get_inspection_plots(args.obs_id, qa_plot_dir,
                             is_calibrator=is_calibrator, cal_id=args.cal_id)
    except Exception as e:
        logger.error(e)
        logger.error("#### Getting inspection plots failed")
    else:
        logger.info("#### Getting inspection plots... Done ({0:.0f}s)".format(
            time.time()-start_time_plots))


if __name__ == "__main__":
    main()

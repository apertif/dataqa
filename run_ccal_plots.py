#!/usr/bin/env python
"""
Script to automatically run crosscal plots.

Requires a scan number. Optionally takes a directory for writing plots.

Full list of options available with
    
    ``python run_ccal_plots.py -h``
"""

from crosscal import crosscal_plots
from scandata import get_default_imagepath
import argparse
from timeit import default_timer as timer
import logging
import os
from apercal.libs import lib

if __name__ == "__main__":

    start = timer()

    parser = argparse.ArgumentParser(description='Generate crosscal QA plots')

    # 1st argument: File name
    parser.add_argument("scan", help='Scan of target field')
    parser.add_argument("fluxcal", help='Fluxcal name')
    parser.add_argument("polcal", help='Polcal name')

    parser.add_argument('-p', '--path', default=None,
                        help='Destination for images')

    parser.add_argument('-b', '--basedir', default=None,
                        help='Data directory')

    # this mode will make the script look only for the beams processed by Apercal on a given node
    parser.add_argument("--trigger_mode", action="store_true", default=False,
                        help='Set it to run Autocal triggering mode automatically after Apercal.')

    args = parser.parse_args()

    # If no path is given change to default QA path
    if args.path is None:
        output_path = get_default_imagepath(args.scan, basedir=args.basedir)

        # check that crosscal qa directory exists
        output_path = "{0:s}crosscal/".format(output_path)

        if not os.path.exists(output_path):
            os.mkdir(output_path)
    else:
        output_path = args.path

    # Create logging file
    lib.setup_logger(
        'debug', logfile='{0:s}run_ccal_plots.log'.format(output_path))
    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.DEBUG)

    # Create crosscal plots
    crosscal_plots.make_all_ccal_plots(
        args.scan, args.fluxcal, args.polcal, output_path=output_path, basedir=args.basedir, trigger_mode=args.trigger_mode)

    end = timer()
    logger.info('Elapsed time to generate cross-calibration data QA inpection plots is {} minutes'.format(
        (end - start)/60.))
    #time in minutes

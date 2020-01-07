from scandata import get_default_imagepath
import argparse
import time
import logging
import os
import glob
import socket
import numpy as np
from PIL import Image
from apercal.libs import lib
from time import time
import pymp
from report.merge_ccal_scal_plots import run_merge_plots

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate crosscal QA plots')

    # 1st argument: File name
    parser.add_argument("scan", help='Scan of target field')

    parser.add_argument("--do_ccal", action="store_true", default=False,
                        help='Set to enable merging of only the crosscal plots')

    parser.add_argument("--do_scal", action="store_true", default=False,
                        help='Set to enable merging of only the selfcal plots')

    parser.add_argument("--run_parallel", action="store_true", default=False,
                        help='Set to run the script in parallel')

    parser.add_argument('-b', '--basedir', default=None,
                        help='Data directory')

    parser.add_argument('--n_cores', default=5,
                        help='Data directory')

    args = parser.parse_args()

    # get the QA directory
    qa_dir = get_default_imagepath(args.scan, basedir=args.basedir)

    # start logging
    # Create logging file

    lib.setup_logger(
        'info', logfile=os.path.join(qa_dir, 'merge_plots.log'))
    logger = logging.getLogger(__name__)

    start_time = time()

    logger.info("#### Merging plots ...")

    try:
        run_merge_plots(
            qa_dir, do_ccal=args.do_ccal, do_scal=args.do_scal, run_parallel=args.run_parallel, n_cores=args.n_cores)
    except Exception as e:
        logger.warning("#### Merging plots ... Failed ({0:.0f}s)".format(
            time()-start_time))
        logger.exception(e)
    else:
        logger.info("#### Merging plots ... Done ({0:.0f}s)".format(
            time()-start_time))

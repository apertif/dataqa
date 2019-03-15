#!/usr/bin/env python
"""
Script to automatically run crosscal plots
Requires a scan number
Optionally takes a directory for writing plots
"""

from dataqa.crosscal import crosscal_plots
from dataqa.scandata import get_default_imagepath
import argparse
from timeit import default_timer as timer

start = timer()

parser = argparse.ArgumentParser(description='Generate crosscal QA plots')

# 1st argument: File name
parser.add_argument("scan", help='Scan of target field')
parser.add_argument("fluxcal", help='Fluxcal name')

parser.add_argument('-p', '--path', default=None,
                    help='Destination for images')

args = parser.parse_args()

# If no path is given change to default QA path
if args.path is None:
    output_path = get_default_imagepath(args.scan)
else:
    output_path = args.path

crosscal_plots.make_all_ccal_plots(args.scan, args.fluxcal, output_path)

end = timer()
print 'Elapsed time to generate cross-calibration data QA inpection plots is {} minutes'.format(
    (end - start)/60.)
#time in minutes

"""
Script to automatically run crosscal plots
Requires a scan number
Optionally takes a directory for writing plots
"""

import os
from selfcal import selfcal_plots as scplots
import argparse
from timeit import default_timer as timer
from dataqa.scandata import get_default_imagepath

start = timer()

parser = argparse.ArgumentParser(description='Generate selfcal QA plots')

# 1st argument: File name
parser.add_argument("scan", help='Scan of target field')
parser.add_argument("target", help='Target name')

parser.add_argument('-p', '--path', default=None,
                    help='Destination for images')

args = parser.parse_args()

# If no path is given change to default QA path
if args.path is None:
    output_path = get_default_imagepath(args.scan)

    # check that selfcal qa directory exists
    output_path = "{0:s}selfcal/".format(output_path)

    if not os.path.exists(output_path):
        os.mkdir(output_path)
else:
    output_path = args.path

# Get phase plots
PH = scplots.PHSols(args.scan, args.target)
PH.get_data()
PH.plot_phase(imagepath=output_path)

print('Done with phase plots')

# Get amp plots
#AMP = scplots.AMPSols(args.scan, args.target)
# AMP.get_data()
# AMP.plot_amp(imagepath=output_path)

# print 'Done with amplitude plots'


#end = timer()
# print 'Elapsed time to generate cross-calibration data QA inpection plots is {} minutes'.format(
#    (end - start)/60.)
#time in minutes

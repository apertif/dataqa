#!/usr/bin/env python
"""
Script to automatically run crosscal plots
Requires a scan number
Optionally takes a directory for writing plots
"""

import os
from crosscal import crosscal_plots as ccplots
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
    home_dir = os.path.expanduser('~')
    output_path = "{0:s}/qa_science_demo_2019/{1:s}/crosscal".format(
        home_dir, args.scan)
else:
    output_path = args.path


# Get BP plots
BP = ccplots.BPSols(args.scan, args.fluxcal)
BP.get_data()
BP.plot_amp(imagepath=output_path)
BP.plot_phase(imagepath=output_path)

print 'Done with bandpass plots'


# Get Gain plots
Gain = ccplots.GainSols(args.scan, args.fluxcal)
Gain.get_data()
Gain.plot_amp(imagepath=output_path)
Gain.plot_phase(imagepath=output_path)

print 'Done with gainplots'

# Get Raw data
Raw = ccplots.RawData(args.scan, args.fluxcal)
Raw.get_data()
Raw.plot_amp(imagepath=output_path)
Raw.plot_phase(imagepath=output_path)

print 'Done with plotting raw data'

# Get model data
Model = ccplots.ModelData(args.scan, args.fluxcal)
Model.get_data()
Model.plot_amp(imagepath=output_path)
Model.plot_phase(imagepath=output_path)

print 'Done with plotting model data'

# Get corrected data
Corrected = ccplots.CorrectedData(args.scan, args.fluxcal)
Corrected.get_data()
Corrected.plot_amp(imagepath=output_path)
Corrected.plot_phase(imagepath=output_path)

print 'Done with plotting corrected data'

end = timer()
print 'Elapsed time to generate cross-calibration data QA inpection plots is {} minutes'.format(
    (end - start)/60.)
#time in minutes

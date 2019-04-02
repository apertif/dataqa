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

start=timer()

parser = argparse.ArgumentParser(description='Run RFInder')

#1st argument: taskID
parser.add_argument("taskID", help='Task ID of target field')

#2nd argument: fluxcal name
parser.add_argument("fluxcal", help='Fluxcal name')

#3rd argument: destination for images, optional
parser.add_argument('-p','--path',default=None,
                    help='Destination for images')

args = parser.parse_args()

# If no path is given change to default QA path
if args.path is None:
    output_path = get_default_imagepath(args.taskID)

    #check that preflag qa directory exists
    output_path = "{0:s}preflag/".format(output_path)

    if not os.path.exists(output_path):
        os.mkdir(output_path)
else:
    output_path = args.path

#Create logging file
lib.setup_logger(
    'debug', logfile='{0:s}run_rfinder.log'.format(output_path))
logger=logging.getLogger(__name__)

#Run RFInder
#iterate over beams
for b in range(40):
    qapath = "{0:s}{1:02d}/".format(output_path,b)
    msfile = '{0:s}.MS'.format(args.fluxcal)
    if not os.path.exists(qapath):
        os.mkdir(qapath)
    if b < 10:
        datapath = '/data/apertif/{0:s}/{1:02d}/raw/'.format(args.taskID,b)        
    if 10 <= b <20:
        datapath = '/data2/apertif/{0:s}/{1:02d}/raw/'.format(args.taskID,b)        
    if 20 <=b <30:
        datapath = '/data3/apertif/{0:s}/{1:02d}/raw/'.format(args.taskID,b)        
    if 30 <= b <40:
        datapath = '/data4/apertif/{0:s}/{1:02d}/raw/'.format(args.taskID,b)        
    rfinder_command = ("python /home/apercal/pipeline/bin/rfinder -idir {0:s} -i {1:s} -tel apertif "
                       "-mode use_flags -odir {2:s} -fl 0 -tStep 5 -yesClp").format(datapath,msfile,qapath)
    #print rfinder_command
    os.system(rfinder_command)

    #move 2D plot to where report can find it (quick & dirty hack)
    old2d = "{0:s}/rfi_q/plots/movies/Time_2Dplot_movie.gif".format(qapath)
    new2d = "{0:s}/Time_2D_{1:s}.png".format(qapath,args.fluxcal)
    oldaa = "{0:s}/rfi_q/plots/movies/AltAz_movie.gif".format(qapath)
    newaa = "{0:s}/test_AltAz_{1:s}.png".format(qapath,args.fluxcal)
    try:
        os.rename(old2d,new2d)
    except:
        pass
    try:
        os.rename(oldaa,newaa)
    except:
        pass
    
end = timer()
logger.info('Elapsed time to run RFinder is {} minutes'.format(
    (end-start)/60.))

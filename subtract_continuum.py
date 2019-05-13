#!/usr/bin/env python


"""
This script does continuum subtraction on line cubes.

- It creates a new fits file in: '/data*/apertif/<obs_id>/<beam>/line/cubes/HI_image_cube_contsub.fits'

Parameter
    obs_id : int
        Observation number which should be assessed

Example:
    python subtract_continuum.py obs_id
"""


import os
import sys
import apercal.libs.lib as lib
import subprocess
import socket
import argparse
import time

# ---------------------------------------
# Create and parse argument list
# ---------------------------------------
parser = argparse.ArgumentParser(
    description='Create mosaic image from pipeline continuum images')

# main argument: Observation number
parser.add_argument("obs_id", type=str,
                    help='Observation Number / Scan Number / TASK-ID')

# this mode will make the script look only for the beams processed by Apercal on a given node
parser.add_argument("--trigger_mode", action="store_true", default=False,
                    help='Set to run for mosaic QA.')

args = parser.parse_args()

# ---------------------------------------
# Check what host the user is on
# ---------------------------------------

host_name = socket.gethostname()

if host_name != "happili-01" and not args.trigger_mode:
    print("WARNING: You are not working on happili-01.")
    print("WARNING: The script will not process all beams")
    print("Please switch to happili-01")
elif args.trigger_mode:
    print(
        "--> Running continuum QA in trigger mode. Looking only for data processed by Apercal on {0:s} <--".format(host_name))

# ---------------------------------------
# Basic parameters
# ---------------------------------------

# get the observation number
data_dir = args.obs_id
print("Running continuum subtraction for {0:s}".format(data_dir))

start_time = time.time()

# ---------------------------------------
# subtract continuum from line cubes
# ---------------------------------------


def subract_cont(data, beams):
    for i in beams:
        if os.path.exists('/'+str(data)+'/apertif/'+str(data_dir)+'/'+str(i)+'/line/cubes/HI_image_cube.fits'):

            print("Processing beam {0}".format(i))

            fits = lib.miriad('fits')
            fits.in_ = '/'+str(data)+'/apertif/'+str(data_dir) + \
                '/'+str(i)+'/line/cubes/HI_image_cube.fits'
            fits.out = '/'+str(data)+'/apertif/'+str(data_dir) + \
                '/'+str(i)+'/line/cubes/HI_image_cube.mir'
            fits.op = 'xyin'
            fits.go()

            contsub = lib.miriad('contsub')
            contsub.in_ = '/'+str(data)+'/apertif/'+str(data_dir) + \
                '/'+str(i)+'/line/cubes/HI_image_cube.mir'
            contsub.mode = 'poly,1'
            contsub.contchan = '"(1,800)"'
            contsub.out = '/'+str(data)+'/apertif/'+str(data_dir) + \
                '/'+str(i)+'/line/cubes/HI_image_cube_contsub.mir'
            contsub.go()

            fits.in_ = '/'+str(data)+'/apertif/'+str(data_dir) + \
                '/'+str(i)+'/line/cubes/HI_image_cube_contsub.mir'
            fits.out = '/'+str(data)+'/apertif/'+str(data_dir) + \
                '/'+str(i)+'/line/cubes/HI_image_cube_contsub.fits'
            fits.op = 'xyout'
            fits.go()

            os.system('rm -rf /'+str(data)+'/apertif/'+str(data_dir) +
                      '/'+str(i)+'/line/cubes/HI_image_cube_contsub.mir')
            os.system('rm -rf /'+str(data)+'/apertif/'+str(data_dir) +
                      '/'+str(i)+'/line/cubes/HI_image_cube.mir')

        # else print('File not found:/'+str(data)+'/apertif/'+str(data_dir)+'/'+str(i)+'/line/cubes/HI_image_cube.fits')


# find beams
if os.path.exists('/data/apertif/'+str(data_dir)) or args.trigger_mode:
    beams_1 = os.listdir('/data/apertif/'+str(data_dir))
    subract_cont('data', beams_1)

if os.path.exists('/data2/apertif/'+str(data_dir)) and not args.trigger_mode:
    beams_2 = os.listdir('/data2/apertif/'+str(data_dir))
    subract_cont('data2', beams_2)

if os.path.exists('/data3/apertif/'+str(data_dir)) and not args.trigger_mode:
    beams_3 = os.listdir('/data3/apertif/'+str(data_dir))
    subract_cont('data3', beams_3)

if os.path.exists('/data4/apertif/'+str(data_dir)) and not args.trigger_mode:
    beams_4 = os.listdir('/data4/apertif/'+str(data_dir))
    subract_cont('data4', beams_4)

print("Finished continuum subtraction ({0:.0f}s)".format(
    time.time() - start_time))

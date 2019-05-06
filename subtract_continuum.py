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

# ---------------------------------------
# subtract continuum from line cubes
# ---------------------------------------


def subract_cont(data, beams):
    """Function to perform the continuum subtraction

    """

    for i in beams:
        if os.path.exists('/'+str(data)+'/apertif/'+str(data_dir)+'/'+str(i)+'/line/cubes/HI_image_cube.fits'):

            fits = lib.miriad('fits')
            fits.in_ = '/'+str(data)+'/apertif/'+str(data_dir)+'/' + \
                str(i)+'/line/cubes/HI_image_cube.fits'
            fits.out = '/'+str(data)+'/apertif/'+str(data_dir)+'/' + \
                str(i)+'/line/cubes/HI_image_cube.mir'
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

            fits.in_ = '/'+str(data)+'/apertif/'+str(data_dir)+'/' + \
                str(i)+'/line/cubes/HI_image_cube_contsub.mir'
            fits.out = '/'+str(data)+'/apertif/'+str(data_dir)+'/' + \
                str(i)+'/line/cubes/HI_image_cube_contsub.fits'
            fits.op = 'xyout'
            fits.go()

            os.system('rm -rf /'+str(data)+'/apertif/'+str(data_dir) +
                      '/'+str(i)+'/line/cubes/HI_image_cube_contsub.mir')
            os.system('rm -rf /'+str(data)+'/apertif/'+str(data_dir) +
                      '/'+str(i)+'/line/cubes/HI_image_cube.mir')

        # else print('File not found:/'+str(data)+'/apertif/'+str(data_dir)+'/'+str(i)+'/line/cubes/HI_image_cube.fits')


if __name__ == "__main__":

    # ---------------------------------------
    # Check what host the user is on
    # ---------------------------------------

    host_name = socket.gethostname()

    if host_name != "happili-01":
        print("WARNING: You are not working on happili-01.")
        print("WARNING: The script will not process all beams")
        print("Please switch to happili-01")

    # ---------------------------------------
    # Create and parse argument list
    # ---------------------------------------
    parser = argparse.ArgumentParser(
        description='Create mosaic image from pipeline continuum images')

    # main argument: Observation number
    parser.add_argument("obs_id", type=str,
                        help='Observation Number / Scan Number / TASK-ID')

    args = parser.parse_args()

    # ---------------------------------------
    # Basic parameters
    # ---------------------------------------

    # get the observation number
    data_dir = args.obs_id
    print(data_dir)

    # find beams
    if os.path.exists('/data/apertif/'+str(data_dir)):
        beams_1 = os.listdir('/data/apertif/'+str(data_dir))
        subract_cont('data', beams_1)

    if os.path.exists('/data2/apertif/'+str(data_dir)):
        beams_2 = os.listdir('/data2/apertif/'+str(data_dir))
        subract_cont('data2', beams_2)

    if os.path.exists('/data3/apertif/'+str(data_dir)):
        beams_3 = os.listdir('/data3/apertif/'+str(data_dir))
        subract_cont('data3', beams_3)

    if os.path.exists('/data4/apertif/'+str(data_dir)):
        beams_4 = os.listdir('/data4/apertif/'+str(data_dir))
        subract_cont('data4', beams_4)

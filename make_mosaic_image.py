#!/usr/bin/env python


"""
This script creates a mosaic file from apertif continuum images.

- This script takes the obs_id as an argument, 
- looks for continuum images from the pipeline (fits format), 
- copies the images into a temporary directory, 
- creates a mosaic image in /data/apertif/obs_id/mosaic/
- and deletes the temporary directory. 

Parameter
    obs_id : int
        Observation number which should be assessed

Example:
    python make_mosaic_image.py obs_id

"""

import os
import sys
import apercal.libs.lib as lib
import subprocess  
import socket
import argparse

#------------------------------------------
#data_dir = '190311152'

#myusername = os.environ['USER']

# Check what host the user is on
#-------------------------------------

host_name = socket.gethostname()

if host_name != "happili-01":
	print("WARNING: You are not working on happili-01.")
	print("WARNING: The script will not process all beams")
	print("Please switch to happili-01")


# Create and parse argument list
#---------------------------------------
parser = argparse.ArgumentParser(
	description='Create mosaic image from pipeline continuum images')

# main argument: Observation number
parser.add_argument("obs_id", type=str,
					help='Observation Number / Scan Number / TASK-ID')

args = parser.parse_args()

# Basic parameters
#-----------------------------------------

# get the observation number
data_dir = args.obs_id
print(data_dir)


#-------------------------------------------
# search for continuum files in standard pipeline directories
# and copy the files into a temporary directory
# if there is no fits file in the continuum folder, there will be an error message, but the script will continue running 

if not os.path.exists('/data/apertif/'+str(data_dir)+'/mosaic/'):
	os.mkdir('/data/apertif/'+str(data_dir)+'/mosaic/')

if not os.path.exists('/data/apertif/'+str(data_dir)+'/mosaic/cont_tmp/'):
	os.mkdir('/data/apertif/'+str(data_dir)+'/mosaic/cont_tmp/')
         

beams_1 = os.listdir('/data/apertif/'+str(data_dir))
beams_2 = os.listdir('/data2/apertif/'+str(data_dir))
beams_3 = os.listdir('/data3/apertif/'+str(data_dir))
beams_4 = os.listdir('/data4/apertif/'+str(data_dir))

#print(beams_1)

def copy_data(beams, n, data):
	for i in beams:
		if os.path.isdir('/'+str(data)+'/apertif/'+str(data_dir)+'/'+str(i)) == True and n in i:
			os.system('cp -r /'+str(data)+'/apertif/'+str(data_dir)+'/'+str(i)+'/continuum/image_mf_*.fits /data/apertif/'+str(data_dir)+'/mosaic/cont_tmp/image_mf_'+str(i)+'.fits') 


copy_data(beams_1, '0', 'data')
copy_data(beams_2, '1', 'data2')
copy_data(beams_3, '2', 'data3')
copy_data(beams_4, '3', 'data4')

#--------------------------------------
# convert fits continuum images into miriad files
# (this may not be needed)

items = os.listdir('/data/apertif/'+str(data_dir)+'/mosaic/cont_tmp/')

def convert_fits():
	for i in range(len(items)):
		fits = lib.miriad('fits')
		fits.in_ = '/data/apertif/'+str(data_dir)+'/mosaic/cont_tmp/'+str(items[i])
		fits.out= '/data/apertif/'+str(data_dir)+'/mosaic/cont_tmp/'+str(items[i][:-5])+'.mir'
		fits.op = 'xyin'
		fits.go()

convert_fits()

#-----------------------------------
# create mosaic image with linmos

print('/data/apertif/'+str(data_dir)+'/mosaic/cont_tmp/image_mf_*.mir')

linmos = lib.miriad('linmos')
linmos.in_ = '/data/apertif/'+str(data_dir)+'/mosaic/cont_tmp/image_mf_*.mir'
linmos.out = '/data/apertif/'+str(data_dir)+'/mosaic/'+str(data_dir)+'_mosaic_image'
linmos.go()

#-----------------------------------
# convert mosaic miriad image into fits file

fits = lib.miriad('fits')
fits.in_ = '/data/apertif/'+str(data_dir)+'/mosaic/'+str(data_dir)+'_mosaic_image'
fits.op = 'xyout'
fits.out = '/data/apertif/'+str(data_dir)+'/mosaic/'+str(data_dir)+'_mosaic_image.fits'
fits.go()

#-------------------------------------
#clen up temporary files

os.system('rm -rf /data/apertif/'+str(data_dir)+'/mosaic/cont_tmp/') 


print("DONE") 
#!/usr/bin/env python

import os
import sys
import apercal.libs.lib as lib
import subprocess  

# create a mosaic file from apertif continuum images 
# this script assumes the output of the automated pipeline 
#------------------------------------------

data_dir = '190311152'

myusername = os.environ['USER']
#print('user:', myusername)

#-------------------------------------------
# search for continuum files in standard pipeline directories
# and copy the files into a temporary directory
# if there is no fits file in the continuum folder, there will be an error message, but the script will continue running 

os.system('mkdir /data/apertif/'+str(data_dir)+'/mosaic/') 
os.system('mkdir /data/apertif/'+str(data_dir)+'/mosaic/continuum_tmp/') 


beams_1 = os.listdir('/data/apertif/'+str(data_dir))
beams_2 = os.listdir('/data2/apertif/'+str(data_dir))
beams_3 = os.listdir('/data3/apertif/'+str(data_dir))
beams_4 = os.listdir('/data4/apertif/'+str(data_dir))

#print(beams_1)

def copy_data(beams, n, data):
	for i in beams:
		if os.path.isdir('/'+str(data)+'/apertif/'+str(data_dir)+'/'+str(i)) == True and n in i:
			os.system('cp -r /'+str(data)+'/apertif/'+str(data_dir)+'/'+str(i)+'/continuum/image_mf_*.fits /data/apertif/'+str(data_dir)+'/mosaic/continuum_tmp/image_mf_'+str(i)+'.fits') 


copy_data(beams_1, '0', 'data')
copy_data(beams_2, '1', 'data2')
copy_data(beams_3, '2', 'data3')
copy_data(beams_4, '3', 'data4')

#--------------------------------------
# convert fits continuum images into miriad files
# (this may not be needed)

items = os.listdir('/data/apertif/'+str(data_dir)+'/mosaic/continuum_tmp/')

def convert_fits():
	for i in range(len(items)):
		fits = lib.miriad('fits')
		fits.in_ = '/data/apertif/'+str(data_dir)+'/mosaic/continuum_tmp/'+str(items[i])
		fits.out= '/data/apertif/'+str(data_dir)+'/mosaic/continuum_tmp/'+str(items[i][:-5])+'.mir'
		fits.op = 'xyin'
		fits.go()

convert_fits()

#-----------------------------------
# create mosaic image with linmos

linmos = lib.miriad('linmos')
linmos.in_ = '/data/apertif/'+str(data_dir)+'/mosaic/continuum_tmp/image_mf_*.mir'
linmos.out= '/data/apertif/'+str(data_dir)+'/mosaic/'+str(data_dir)+'_mosaick_image'
linmos.go()

#-----------------------------------
# convert mosaic miriad image into fits file

fits = lib.miriad('fits')
fits.in_ = '/data/apertif/'+str(data_dir)+'/mosaic/'+str(data_dir)+'_mosaick_image'
fits.op = 'xyout'
fits.out = '/data/apertif/'+str(data_dir)+'/mosaic/'+str(data_dir)+'_mosaick_image.fits'
fits.go()

#-------------------------------------
#clen up temporary files

os.system('rm -rf /data/apertif/'+str(data_dir)+'/mosaic/continuum_tmp/') 


print("DONE") 
#!/usr/bin/env python

import glob
import os
import numpy as np
import logging

#----------------------------------------------
# read data from np file

logger = logging.getLogger(__name__)

def simplify_data(d, beamnum):
	"""
	select relevant beam value from a list in a dictionary
	"""
	dict = {}
	
	for k in d.keys():
		if np.iterable(d[k]) and len(d[k]) == 40:
			dict.update({k:d[k][beamnum]})
		else:
			dict.update({k:d[k]})

	return dict


def extract_data(path, beamnum, module, source):
	"""
    Function to return numpy files contents as a dictionary filtered for certain keys
    Args:
        path (str): Directory of the data 
        beamnum (int): Beam number
        module (str): name of the apercal module e.g. 'preflag', 'convert', 'croscal'
        source (str): name of the source or calibrators for preflag, for other modules it should be an empty string ('')

    Returns
        a dictionary with information extracted from a numpy log file
    """
	
	#logger.info('Checking NPY files for beam {}'.format(beamnum))

	f = glob.glob(os.path.join(path, 'param_{:02d}*{}*{}.npy'.format(beamnum, module, source)))
	res = {}
	dict_cut = {}
	
	if len(f) != 0:
		d = np.load(f[0]).item()


		for k in d.keys(): 
			if module == 'preflag' and "targetbeams" in k:
				res.update({k:d[k]})

			if module == 'crosscal':
				res.update({k:d[k]})

			if module == 'convert' and "UVFITS2MIRIAD" in k:
				res.update({k:d[k]})

			if module == 'convert' and "MS2UVFITS" in k:
				res.update({k:d[k]})

		dict_cut = simplify_data(res, beamnum)
	
	else:	
		#print('No file for beam: ', i)
		logging.info("No file for beam: {}".format(beamnum))
		
	logging.info("Extracting data ... Done")

	return dict_cut
	
	

#!/usr/bin/env python

import glob
import os
import numpy as np
import logging
from make_nptabel_summary import extract_data

#------------------------------------------------- 
beams_1 = '/data/apertif/190602049/'
module = 'preflag' 
source = 'LH_GRG'
 
for i in range(9):
	beam_info = extract_data(beams_1, i, module, source)  
	print(module, i, beam_info) 
#!/usr/bin/env python

import glob
import os
import numpy as np
import logging
from make_nptabel_summary import extract_all_beams, find_sources, make_csv
import csv

#------------------------------------------------- 
beams_1 = '/data/apertif/190602049/'
obs_id = '190602049'
module = 'preflag' 
#source = 'LH_GRG'
 

beam_info = extract_all_beams(obs_id, module)  
print(beam_info[1]['beam'])
print(len(beam_info))

#print(beam_info)

#print(find_sources(obs_id))
make_csv(obs_id, module)
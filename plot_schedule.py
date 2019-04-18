#!/usr/bin/env python

"""
This script visualises the observing schedule by producing elevation and HA plots as a function of time. 
Using pandas, astropy and matplotlib.

Parameter
    obs_id : str
        csv file with the schedule.

Example:
    python plot_schedule.py schedule.csv

"""

import argparse
import numpy as np
from astropy.coordinates import EarthLocation, AltAz, ICRS, SkyCoord, FK5, Galactic
import astropy.units as u
from astropy.time import Time
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['xtick.direction']='in'
mpl.rcParams['ytick.direction']='in'

#--------------------------------------------------
# Create and parse argument list
#--------------------------------------------------
parser = argparse.ArgumentParser(
	description='Plot shedule')

# main argument: schedule file
parser.add_argument("sched_file", type=str,
					help='schedule file (.csv)')

args = parser.parse_args()

schedule_file = args.sched_file
#schedule_file = 'imaging_sched_longcal_ppmod30_04-08_21h_EAKA.csv'

#--------------------------------------------------
# Basic parameters
#--------------------------------------------------
WSRT = EarthLocation.of_address("Westerbork radio telescope")

data = pd.read_csv(schedule_file) 
#--------------------------------------------------
def add_12(vals):
    for i in range(len(vals)):
        if vals[i] > 12:
            vals[i] = vals[i] - 24
            
        if vals[i] < -12:
            vals[i] = vals[i] + 24
            
#--------------------------------------------------
# calculate relavant values for the plot
#--------------------------------------------------

data['time_1'] = data.apply (lambda row: Time(str(row['date1'])+'T'+str(row['time1'])), axis=1)
data['time_2'] = data.apply (lambda row: Time(str(row['date2'])+'T'+str(row['time2'])), axis=1)
data['obs_length'] = data.apply (lambda row: (row['time_2'] - row['time_1']).to(u.h).value, axis=1)
data['timespan'] = data.apply (lambda row: row['time_1'] + np.linspace(0, row['obs_length'], 100)*u.hour, axis=1)

data['altazframe'] = data.apply (lambda row: AltAz(location=WSRT, obstime=row['timespan']), axis=1)
data['my_obj'] = data.apply (lambda row: SkyCoord(ra=row['ra'], dec=row['dec'], unit=(u.hourangle, u.deg)), axis=1)
data['my_obj_altaz'] = data.apply (lambda row: row['my_obj'].transform_to(row['altazframe']), axis=1)

data['my_obj_fk5'] = data.apply (lambda row: row['my_obj'].transform_to(FK5(equinox=row['timespan'])), axis=1)
data['my_obj_HA'] = data.apply (lambda row: row['my_obj_fk5'].ra - row['timespan'].sidereal_time('apparent', longitude =WSRT.lon), axis=1)
data['LST'] = data.apply (lambda row: row['timespan'].sidereal_time('apparent', longitude =WSRT.lon), axis=1)
data['my_obj_LHA'] = data.apply (lambda row: row['timespan'].sidereal_time('apparent', longitude =WSRT.lon) - row['my_obj_fk5'].ra, axis=1)
data['my_obj_LHA_2'] = data.apply (lambda row: add_12(row['my_obj_LHA'].value), axis=1)

#--------------------------------------------------
# make elevation plot
#--------------------------------------------------

fig, ax = plt.subplots(figsize=[8,5])
ax.set_title(schedule_file)
for i in (range(len(data['date1']))):
    ax.plot(data['timespan'][i].datetime, data['my_obj_altaz'][i].alt, label=data['source'][i])

ax.grid(True, alpha=0.3)
ax.set_ylim(0,90)
ax.set_ylabel('Elevation')
ax.set_xlabel('Date and time')
ax.axhline(y=20, c='r', linestyle='--')
ax.legend(bbox_to_anchor=(1.03, 1.05))
plt.savefig(schedule_file[:-4]+'_elevation.png', bbox_inches='tight', dpi=200)


#--------------------------------------------------
# make LHA plot
#--------------------------------------------------
fig, ax = plt.subplots(figsize=[8,5])
ax.set_title(schedule_file)
for i in (range(len(data['date1']))):
    ax.plot(data['timespan'][i].datetime, data['my_obj_LHA'][i], label=data['source'][i])

ax.grid(True, alpha=0.3)
#ax.set_ylim(0,90)
ax.set_ylabel('HA')
ax.set_xlabel('Date and time')
ax.axhline(y=6, c='r', linestyle='--')
ax.axhline(y=-6, c='r', linestyle='--')
ax.axhline(y=3.3, c='grey', linestyle='--')
ax.axhline(y=-3.3, c='grey', linestyle='--')
ax.legend(bbox_to_anchor=(1.03, 1.05))
plt.savefig(schedule_file[:-4]+'_LHA.png', bbox_inches='tight', dpi=200)

print('DONE')
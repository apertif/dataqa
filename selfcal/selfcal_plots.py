# python "module" for QA plots for cross-cal
# Will want to plot calibration solutions
# also potential for raw and corrected data

# load necessary packages
import os
import numpy as np
from apercal.subs import readmirlog
from apercal.subs import misc
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from ..scandata import ScanData


class PHSols(ScanData):
    def __init__(self, scan, target):
        ScanData.__init__(self, scan, target)
        self.phants = np.empty(len(self.dirlist), dtype=np.object)
        self.phtimes = np.empty(len(self.dirlist), dtype=np.object)
        self.phases = np.empty(len(self.dirlist), dtype=np.ndarray)
        self.phnants = np.empty(len(self.dirlist), dtype=np.ndarray)
        self.phnbins = np.empty(len(self.dirlist), dtype=np.ndarray)
        self.phnsols = np.empty(len(self.dirlist), dtype=np.ndarray)

    def get_data(self):
        # get the data
        for i, (path, beam) in enumerate(zip(self.dirlist, self.beamlist)):
            phdata = "{0}/selfcal/{1}.mir".format(path, self.sourcename)
            if os.path.isdir(phdata):
                phgains, times = readmirlog.get_phases(phdata)
                self.phants[i] = misc.create_antnames()
                self.phtimes[i] = times
                self.phases[i] = phgains
                self.phnants[i], self.phnbins[i], self.phnsols[i] = readmirlog.get_ndims(phdata)
            else:
                print 'Filling with NaNs. Phase self-calibration not present for B{}'.format(beam)
                self.phants[i] = misc.create_antnames()
                self.phtimes[i] = np.array(np.nan)
                self.phases[i] = np.array(np.nan)
                self.phnbins[i] = np.array(np.nan)
                self.phnants[i], self.phnbins[i], self.phnsols[i] = np.array(np.nan), np.array(np.nan), np.array(np.nan)

    def plot_phase(self, imagepath=None):
        """Plot phase, one plot per antenna"""
        imagepath = self.create_imagepath(imagepath)
        ant_names = self.ants[0]
        for a, ant in enumerate(ant_names):
            # iterate through antennas
            # set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx * 4
            ysize = ny * 4
            plt.figure(figsize=(xsize, ysize))
            plt.suptitle('Selfcal phases for Antenna {0}'.format(ant))

            for n, beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum + 1)
                color = cm.rainbow(np.linspace(0, 1, self.phnbins[n]))
                for f, freqbin, i, c in enumerate(self.phnbins), zip(range(self.phnbins[n], color)):
                    plt.scatter(self.times[n][f], self.phases[n][a, f, :], label='F'+str(f), marker=',', s=1, c=color)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(-180, 180)
            plt.legend()
            plt.savefig('{2}/SCAL_phase_{0}_{1}.png'.format(ant, self.scan, imagepath))
            plt.clf()

class AMPSols(ScanData):
    def __init__(self, scan, target):
        ScanData.__init__(self, scan, target)
        self.ampants = np.empty(len(self.dirlist), dtype=np.object)
        self.amptimes = np.empty(len(self.dirlist), dtype=np.object)
        self.amps = np.empty(len(self.dirlist), dtype=np.ndarray)


    def get_data(self):
        for i, (path, beam) in enumerate(zip(self.dirlist, self.beamlist)):
            ampdata = "{0}/selfcal/{1}_amp.mir".format(path, self.sourcename)
            if os.path.isdir(ampdata):
                times, ampgains = readmirlog.get_gains(ampdata)
                self.ampants = misc.create_antnames()
                self.amptimes[i] = times
                self.amps[i] = ampgains
            else:
                print 'Filling with NaNs. Amplitude self-calibration not present for B{}'.format(beam)
                self.ampants[i] = misc.create_antnames()
                self.amptimes[i] = np.array(np.nan)
                self.amps[i] = np.array(np.nan)

    def plot_amp(self, imagepath=None):
        """Plot amplitude, one plot per antenna"""
        Imagepath = self.create_imagepath(imagepath)
        # put plots in default place w/ default name
        ant_names = self.ampants[0]
        # figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        for a, ant in enumerate(ant_names):
            # iterate through antennas
            # set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx * 4
            ysize = ny * 4
            plt.figure(figsize=(xsize, ysize))
            plt.suptitle('Bandpass amplitude for Antenna {0}'.format(ant), size=20)

            for n, beam in enumerate(self.beamlist):
                beamnum = int(beam)
                # print beamnum
                plt.subplot(ny, nx, beamnum + 1)
                plt.scatter(self.freq[n][0, :], self.amp[n][a, :, 0], label='XX', marker=',', s=1)
                plt.scatter(self.freq[n][0, :], self.amp[n][a, :, 1], label='YY', marker=',', s=1)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(0, 1.8)
            plt.legend()
            plt.savefig('{2}/BP_amp_{0}_{1}.png'.format(ant, self.scan, imagepath))
            plt.clf()

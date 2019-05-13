# python "module" for QA plots for cross-cal
# Will want to plot calibration solutions
# also potential for raw and corrected data

# load necessary packages
import os
import numpy as np
import datetime
from apercal.subs import readmirlog
from apercal.subs import misc
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from scandata import ScanData


class PHSols(ScanData):
    def __init__(self, scan, target, trigger_mode=False):
        ScanData.__init__(self, scan, target, trigger_mode=trigger_mode)
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
                try:
                    phgains, times = readmirlog.get_phases(phdata)
                    self.phants[i] = misc.create_antnames()
                    self.phtimes[i] = times
                    self.phases[i] = phgains
                    self.phnants[i], self.phnbins[i], self.phnsols[i] = readmirlog.get_ndims(
                        phdata)
                except:
                    print 'Filling with NaNs. Phase self-calibration not present for B{}'.format(beam)
                    self.phants[i] = misc.create_antnames()
                    self.phtimes[i] = np.array(np.nan)
                    self.phases[i] = np.array(np.nan)
                    self.phnbins[i] = np.array(np.nan)
                    self.phnants[i], self.phnbins[i], self.phnsols[i] = np.array(
                        np.nan), np.array(np.nan), np.array(np.nan)
            else:
                print 'Filling with NaNs. Phase self-calibration not present for B{}'.format(beam)
                self.phants[i] = misc.create_antnames()
                self.phtimes[i] = np.array(np.nan)
                self.phases[i] = np.array(np.nan)
                self.phnbins[i] = np.array(np.nan)
                self.phnants[i], self.phnbins[i], self.phnsols[i] = np.array(
                    np.nan), np.array(np.nan), np.array(np.nan)

    def plot_phase(self, imagepath=None):
        """Plot phase, one plot per antenna"""
        imagepath = self.create_imagepath(imagepath)
        ant_names = misc.create_antnames()
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
                if np.isnan(self.phnbins[n]):
                    continue
                else:
                    color = cm.rainbow(np.linspace(0, 1, self.phnbins[n]))
                    for f in range(self.phnbins[n]):
                        plt.scatter(range(len(
                            self.phtimes[n])), self.phases[n][a, f, :], label='F'+str(f), marker=',', s=1, c=color[f])
                        if n >= 32:
                            plt.xlabel('Time [solint]')
                        if n % nx == 0:
                            plt.ylabel('Phase [deg]')

                plt.title('Beam {0}'.format(beam))
            plt.legend(prop={'size': 5})

            plt.savefig(
                '{2}SCAL_phase_{0}_{1}.png'.format(ant, self.scan, imagepath))
            plt.close("all")


class AMPSols(ScanData):
    def __init__(self, scan, target, trigger_mode=False):
        ScanData.__init__(self, scan, target, trigger_mode=trigger_mode)
        self.ampants = np.empty(len(self.dirlist), dtype=np.object)
        self.amptimes = np.empty(len(self.dirlist), dtype=np.object)
        self.amps = np.empty(len(self.dirlist), dtype=np.ndarray)
        self.ampnants = np.empty(len(self.dirlist), dtype=np.ndarray)
        self.ampnbins = np.empty(len(self.dirlist), dtype=np.ndarray)
        self.ampnsols = np.empty(len(self.dirlist), dtype=np.ndarray)

    def get_data(self):
        for i, (path, beam) in enumerate(zip(self.dirlist, self.beamlist)):
            ampdata = "{0}/selfcal/{1}_amp.mir".format(path, self.sourcename)
            if os.path.isdir(ampdata):
                try:
                    ampgains, times = readmirlog.get_phases(ampdata)
                    self.ampants[i] = misc.create_antnames()
                    self.amptimes[i] = times
                    self.amps[i] = ampgains
                    self.ampnants[i], self.ampnbins[i], self.ampnsols[i] = readmirlog.get_ndims(
                        ampdata)
                except:
                    print 'Filling with NaNs. Amplitude self-calibration not present for B{}'.format(beam)
                    self.ampants[i] = misc.create_antnames()
                    self.amptimes[i] = np.array(np.nan)
                    self.amps[i] = np.array(np.nan)
                    self.ampnbins[i] = np.array(np.nan)
                    self.ampnants[i], self.ampnbins[i], self.ampnsols[i] = np.array(
                        np.nan), np.array(np.nan), np.array(np.nan)
            else:
                print 'Filling with NaNs. Amplitude self-calibration not present for B{}'.format(beam)
                self.ampants[i] = misc.create_antnames()
                self.amptimes[i] = np.array(np.nan)
                self.amps[i] = np.array(np.nan)
                self.ampnbins[i] = np.array(np.nan)
                self.ampnants[i], self.ampnbins[i], self.ampnsols[i] = np.array(
                    np.nan), np.array(np.nan), np.array(np.nan)

    def plot_amp(self, imagepath=None):
        """Plot phase, one plot per antenna"""
        imagepath = self.create_imagepath(imagepath)
        ant_names = misc.create_antnames()
        for a, ant in enumerate(ant_names):
            # iterate through antennas
            # set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx * 4
            ysize = ny * 4
            plt.figure(figsize=(xsize, ysize))
            plt.suptitle('Selfcal amplitudes for Antenna {0}'.format(ant))

            for n, beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum + 1)
                if np.isnan(self.ampnbins[n]):
                    continue
                else:
                    color = cm.rainbow(np.linspace(0, 1, self.ampnbins[n]))
                    for f in range(self.ampnbins[n]):
                        plt.scatter(range(len(
                            self.amptimes[n])), self.amps[n][a, f, :], label='F' + str(f), marker=',', s=1, c=color[f])
                        if n >= 32:
                            plt.xlabel('Time [solint]')
                        if n % nx == 0:
                            plt.ylabel('Amp')

                plt.title('Beam {0}'.format(beam))
            plt.legend()

            plt.savefig('{2}SCAL_amp_{0}_{1}.png'.format(
                ant, self.scan, imagepath))
            plt.close("all")

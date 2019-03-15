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

"""
Define object classes for holding data related to scans
The key thing to specify an object is the scan of the target field
Also need name of fluxcal (for cross-cal solutions)
Want to add functionality for pol-cal for pol solutions (secondary)
This specifies the location of all data, assuming setup of automatic pipeline
(/data/apertif, distributed across happili nodes)
"""


class ScanData(object):
    # Initilailze with source name, scalist and beamlist
    # and place holders for phase and amplitude
    def __init__(self, scan, target):
        self.scan = scan
        self.target = target
        # check if fluxcal is given as 3CXXX.MS or 3CXXX
        # Fix to not include .MS no matter what
        if self.target[-2:] == 'MS':
            self.target = self.target[:-3] + '.mir'
        else:
            self.target = self.target + '.mir'
        # also get a directory list and beamlist
        self.dirlist = []
        self.beamlist = []
        # first check what happili node on
        # if not happili-01, print a warning and only search locally
        hostname = os.uname()[1]
        if hostname != 'happili-01':
            print 'Not on happili-01, only search local {} for data'.format(hostname)
            path = '/data/apertif/{}'.format(self.scan)
            allfiles = os.listdir(path)
            for f in allfiles:
                full_path = os.path.join(path, f)
                if os.path.isdir(full_path):
                    self.dirlist.append(full_path)
                    # create a list of all directories with full path.
                    # This should be all beams - there should be no other directories
                    # f is a string, so add to beam list to also track info about beams
                    self.beamlist.append(f)
        else:
            # On happili-01, so search all nodes
            # ignoring happili-05 - may have to fix this eventually
            path = '/data/apertif/{}'.format(self.scan)
            path2 = '/data2/apertif/{}'.format(self.scan)
            path3 = '/data3/apertif/{}'.format(self.scan)
            path4 = '/data4/apertif/{}'.format(self.scan)
            files01 = os.listdir(path)
            files02 = os.listdir(path2)
            files03 = os.listdir(path3)
            files04 = os.listdir(path4)
            # have to go through one by one - easiest
            for f in files01:
                full_path = os.path.join(path, f)
                if os.path.isdir(full_path):
                    self.dirlist.append(full_path)
                    # also add to beamlist
                    self.beamlist.append(f)
            for f in files02:
                full_path = os.path.join(path2, f)
                if os.path.isdir(full_path):
                    self.dirlist.append(full_path)
                    # also add to beamlist
                    self.beamlist.append(f)
            for f in files03:
                full_path = os.path.join(path3, f)
                if os.path.isdir(full_path):
                    self.dirlist.append(full_path)
                    # also add to beamlist
                    self.beamlist.append(f)
            for f in files04:
                full_path = os.path.join(path4, f)
                if os.path.isdir(full_path):
                    self.dirlist.append(full_path)
                    # also add to beamlist
                    self.beamlist.append(f)  # initialize phase & amp arrays - common to all types of solutions
        self.phase = np.empty(len(self.dirlist), dtype=np.ndarray)
        self.amp = np.empty(len(self.dirlist), dtype=np.ndarray)


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
            phdata = "{0}/selfcal/{1}".format(path, self.target)
            if os.path.isdir(phdata):
                phgains, times = readmirlog.get_phases(phdata)
                self.phants[i] = misc.create_antnames()
                self.phtimes[i] = times
                self.phases[i] = phgains
                self.phnants[i], self.phnbins[i], self.phnsols[i] = readmirlog.get_dims(phdata)
            else:
                print 'Filling with NaNs. Phase self-calibration not present for B{}'.format(beam)
                self.phants[i] = misc.create_antnames()
                self.phtimes[i] = np.array(np.nan)
                self.phases[i] = np.array(np.nan)
                self.phnbins[i] = np.array(np.nan)
                self.phnants[i], self.phnbins[i], self.phnsols[i] = np.array(np.nan), np.array(np.nan), np.array(np.nan)

    def plot_phase(self, imagepath=None):
        # plot phase, one plot per antenna
        # first define imagepath if not given by user
        if imagepath == None:
            # write in user's home directory (know that have write access there)
            myusername = os.environ['USER']
            imagepath = '/home/{}/dataqa_plots'.format(myusername)
        # check if imagepath exists, create if necessary
        if not os.path.exists(imagepath):
            print "{} doesn't exist, creating".format(imagepath)
            os.makedirs(imagepath)
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
            ampdata = "{0}/selfcal/{1}".format(path, self.target.replace('.mir', '_amp.mir'))
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
        # first define imagepath if not given by user
        if imagepath == None:
            # write in user's home directory (know that have write access there)
            myusername = os.environ['USER']
            imagepath = '/home/{}/dataqa_plots'.format(myusername)
        # check if imagepath exists, create if necessary
        if not os.path.exists(imagepath):
            print "{} doesn't exist, creating".format(imagepath)
            os.makedirs(imagepath)
        # plot amplitude, one plot per antenna
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







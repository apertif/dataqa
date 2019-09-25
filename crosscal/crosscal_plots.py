#python "module" for QA plots for cross-cal
#Will want to plot calibration solutions
#also potential for raw and corrected data

from __future__ import print_function

#load necessary packages
import os
import numpy as np
from astropy.io import ascii
import apercal
import casacore.tables as pt
import logging
import matplotlib
import time
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scandata import ScanData
from apercal.subs import misc

logger = logging.getLogger(__name__)

def make_all_ccal_plots(scan, fluxcal, polcal, output_path=None, trigger_mode=False):
    """
    Create crosscal QA plots

    Args:
        scan (int): Task id of target, e.g. 190311152
        fluxcal (str): Name of fluxcal, e.g. "3C147"
        polcal(str): Name of the polcal, e.g. "3C286"
        output_path (str): Output path, None for default
        trigger_mode (bool): To run automatically after Apercal
    """

    # Get autocorrelation plots
    start_time_autocorr = time.time()
    AC = AutocorrData(scan, fluxcal, trigger_mode)
    AC.get_data()
    # create a subdirectory for the autocorrelation plots
    autocorr_plot_dir = os.path.join(output_path, "autocorrelation")
    if not os.path.exists(autocorr_plot_dir):
        os.mkdir(autocorr_plot_dir)
    AC.plot_autocorr_per_antenna(imagepath=autocorr_plot_dir)
    AC.plot_autocorr_per_beam(imagepath=autocorr_plot_dir)
    logger.info('Done with autocorrelation plots ({0:.0f}s)'.format(
        time.time() - start_time_autocorr))

    # just for debugging, remove when done.
    return None

    # Get BP plots
    start_time_bp = time.time()
    BP = BPSols(scan, fluxcal, trigger_mode)
    BP.get_data()
    BP.plot_amp(imagepath=output_path)
    BP.plot_phase(imagepath=output_path)
    logger.info('Done with bandpass plots ({0:.0f}s)'.format(time.time() - start_time_bp))

    # Get Gain plots
    start_time_gain = time.time()
    Gain = GainSols(scan, fluxcal, trigger_mode)
    Gain.get_data()
    Gain.plot_amp(imagepath=output_path)
    Gain.plot_phase(imagepath=output_path)
    logger.info('Done with gainplots ({0:.0f}s)'.format(time.time() - start_time_gain))

    # Get Global Delay plots
    start_time_gdelay = time.time()
    GD = GDSols(scan, fluxcal, trigger_mode)
    GD.get_data()
    GD.plot_delay(imagepath=output_path)
    logger.info('Done with global delay plots ({0:.0f}s)'.format(time.time() - start_time_gdelay))

    # Get polarisation leakage plots
    start_time_leak = time.time()
    Leak = LeakSols(scan, fluxcal, trigger_mode)
    Leak.get_data()
    Leak.plot_amp(imagepath=output_path)
    Leak.plot_phase(imagepath=output_path)
    logger.info('Done with leakage plots ({0:.0f}s)'.format(time.time() - start_time_leak))

    # Get cross hand delay solutions
    start_time_kcross = time.time()
    KCross = KCrossSols(scan, polcal, trigger_mode)
    KCross.get_data()
    KCross.plot_delay(imagepath=output_path)
    logger.info('Done with cross hand delay plots ({0:.0f}s)'.format(time.time() - start_time_kcross))

    # Get polarisation angle plots
    start_time_polangle = time.time()
    Polangle = PolangleSols(scan, polcal, trigger_mode)
    Polangle.get_data()
    Polangle.plot_amp(imagepath=output_path)
    Polangle.plot_phase(imagepath=output_path)
    logger.info('Done with polarisation angle correction plots ({0:.0f}s)'.format(time.time() - start_time_polangle))

    # Get Raw data
    start_time_raw = time.time()
    Raw = RawData(scan, fluxcal, trigger_mode)
    Raw.get_data()
    Raw.plot_amp(imagepath=output_path)
    Raw.plot_phase(imagepath=output_path)
    logger.info('Done with plotting raw data ({0:.0f}s)'.format(
        time.time() - start_time_raw))

    # Get model data
    start_time_model = time.time()
    Model = ModelData(scan, fluxcal, trigger_mode)
    Model.get_data()
    Model.plot_amp(imagepath=output_path)
    Model.plot_phase(imagepath=output_path)
    logger.info('Done with plotting model data  ({0:.0f}s)'.format(
        time.time() - start_time_model))

    # Get corrected data
    start_time_corrected = time.time()
    Corrected = CorrectedData(scan, fluxcal, trigger_mode)
    Corrected.get_data()
    Corrected.plot_amp(imagepath=output_path)
    Corrected.plot_phase(imagepath=output_path)
    logger.info('Done with plotting corrected data  ({0:.0f}s)'.format(
        time.time() - start_time_corrected))


class BPSols(ScanData):
    def __init__(self,scan,fluxcal,trigger_mode):
        ScanData.__init__(self,scan,fluxcal,trigger_mode=trigger_mode)
        self.imagepathsuffix = "crosscal"
        self.ants = np.empty(len(self.dirlist),dtype=np.object)
        self.time = np.empty(len(self.dirlist),dtype=np.ndarray)
        self.freq = np.empty(len(self.dirlist),dtype=np.ndarray)
        self.flags = np.empty(len(self.dirlist),dtype=np.ndarray)
        self.amps_norm = np.empty(len(self.dirlist),dtype=np.ndarray)
        self.phases_norm = np.empty(len(self.dirlist),dtype=np.ndarray)
    
    def get_data(self):
        #get the data
        for i, (path,beam) in enumerate(zip(self.dirlist,self.beamlist)):
            bptable = "{0}/raw/{1}.Bscan".format(path,self.sourcename)
            #print(bptable)
            if os.path.isdir(bptable):
                taql_command = ("SELECT TIME,abs(CPARAM) AS amp, arg(CPARAM) AS phase, "
                                "FLAG FROM {0}").format(bptable)
                t=pt.taql(taql_command)
                times = t.getcol('TIME')
                amp_sols=t.getcol('amp')
                phase_sols = t.getcol('phase')
                flags = t.getcol('FLAG')
                taql_antnames = "SELECT NAME FROM {0}::ANTENNA".format(bptable)
                t= pt.taql(taql_antnames)
                ant_names=t.getcol("NAME") 
                taql_freq = "SELECT CHAN_FREQ FROM {0}::SPECTRAL_WINDOW".format(bptable)
                t = pt.taql(taql_freq)
                freqs = t.getcol('CHAN_FREQ')
            
                #check for flags and mask
                amp_sols[flags] = np.nan
                phase_sols[flags] = np.nan
                
                self.ants[i] = ant_names
                self.time[i] = times
                self.phase[i] = phase_sols *180./np.pi #put into degrees
                self.amp[i] = amp_sols
                self.flags[i] = flags
                self.freq[i] = freqs
                
            else:
                logger.info('Filling with NaNs. BP table not present for B{}'.format(beam))
                self.ants[i] = ['RT2','RT3','RT4','RT5','RT6','RT7','RT8','RT9','RTA','RTB','RTC','RTD']
                self.time[i] = np.array(np.nan)
                self.phase[i] = np.full((12,2,2),np.nan)
                self.amp[i] = np.full((12,2,2),np.nan)
                self.freq[i] = np.full((2,2),np.nan)
            
    def plot_amp(self, imagepath=None):
        """Plot amplitude, one plot per antenna"""

        logging.info("Creating plots for bandpass amplitude")
        imagepath = self.create_imagepath(imagepath)
        #put plots in default place w/ default name
        ant_names = self.ants[0]
        #figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        for a,ant in enumerate(ant_names):
            #iterate through antennas
            #set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx*4
            ysize = ny*4
            plt.figure(figsize=(xsize,ysize))
            plt.suptitle('Bandpass amplitude for Antenna {0}'.format(ant),size=30)
            
            for n,beam in enumerate(self.beamlist):
                beamnum = int(beam)
                #print(beamnum)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(self.freq[n][0,:],self.amp[n][a,:,0],
                            label='XX',
                            marker=',',s=1)
                plt.scatter(self.freq[n][0,:],self.amp[n][a,:,1],
                            label='YY',
                            marker=',',s=1)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(0,1.8)
            plt.legend(markerscale=3,fontsize=14)
            plt.savefig('{imagepath}/BP_amp_{ant}_{scan}.png'.format(ant=ant, scan=self.scan, imagepath=imagepath))
            #plt.clf()
            # to really close the plot, this will do
            plt.close('all')
            
    def plot_phase(self, imagepath=None):
        """Plot phase, one plot per antenna"""

        logger.info("Creating plots for bandpass phase")
        
        imagepath = self.create_imagepath(imagepath)
        ant_names = self.ants[0]
        #figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        for a,ant in enumerate(ant_names):
            #iterate through antennas
            #set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx*4
            ysize = ny*4
            plt.figure(figsize=(xsize,ysize))
            plt.suptitle('Bandpass phases for Antenna {0}'.format(ant),size=30)
            
            for n,beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(self.freq[n][0,:],self.phase[n][a,:,0],
                            label='XX',
                            marker=',',s=1)
                plt.scatter(self.freq[n][0,:],self.phase[n][a,:,1],
                            label='YY',
                            marker=',',s=1)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(-180,180)
            plt.legend(markerscale=3,fontsize=14)
            plt.savefig('{imagepath}/BP_phase_{ant}_{scan}.png'.format(ant=ant,scan=self.scan,imagepath=imagepath))
            #plt.clf()
            # to really close the plot, this will do
            plt.close('all')
            

class GainSols(ScanData):
    def __init__(self,scan,fluxcal,trigger_mode):
        ScanData.__init__(self,scan,fluxcal,trigger_mode=trigger_mode)
        self.imagepathsuffix = "crosscal"
        self.ants = np.empty(len(self.dirlist),dtype=np.object)
        self.time = np.empty(len(self.dirlist),dtype=np.ndarray)
        self.flags = np.empty(len(self.dirlist),dtype=np.ndarray)
        self.amps_norm = np.empty(len(self.dirlist),dtype=np.ndarray)
        self.phases_norm = np.empty(len(self.dirlist),dtype=np.ndarray)
        
    def get_data(self):
        for i, (path,beam) in enumerate(zip(self.dirlist,self.beamlist)):
            gaintable = "{0}/raw/{1}.G1ap".format(path,self.sourcename)
            #check if table exists
            #otherwise, place NaNs in place for everything
            if os.path.isdir(gaintable):
                taql_antnames = "SELECT NAME FROM {0}::ANTENNA".format(gaintable)
                t= pt.taql(taql_antnames)
                ant_names=t.getcol("NAME")
    
                #then get number of times
                #need this for setting shape
                taql_time =  "select TIME from {0} orderby unique TIME".format(gaintable)
                t= pt.taql(taql_time)
                times = t.getcol('TIME') 
    
                #then iterate over antenna
                #set array sahpe to be [n_ant,n_time,n_stokes]
                #how can I get n_stokes? Could be 2 or 4, want to find from data
                #get 1 data entry
                taql_stokes = "SELECT abs(CPARAM) AS amp from {0} limit 1" .format(gaintable)
                t_pol = pt.taql(taql_stokes)
                pol_array = t_pol.getcol('amp')
                n_stokes = pol_array.shape[2] #shape is time, one, nstokes
    
                amp_ant_array = np.empty((len(ant_names),len(times),n_stokes),dtype=object)
                phase_ant_array = np.empty((len(ant_names),len(times),n_stokes),dtype=object)
                flags_ant_array = np.empty((len(ant_names),len(times),n_stokes),dtype=bool)
        
                for ant in xrange(len(ant_names)):
                    taql_command = ("SELECT abs(CPARAM) AS amp, arg(CPARAM) AS phase, FLAG FROM {0} " 
                                    "WHERE ANTENNA1={1}").format(gaintable,ant)
                    t = pt.taql(taql_command)
                    amp_ant_array[ant,:,:] = t.getcol('amp')[:,0,:]
                    phase_ant_array[ant,:,:] = t.getcol('phase')[:,0,:]
                    flags_ant_array[ant,:,:] = t.getcol('FLAG')[:,0,:]
                
                #check for flags and mask
                amp_ant_array[flags_ant_array] = np.nan
                phase_ant_array[flags_ant_array] = np.nan
            
                self.amp[i] = amp_ant_array
                self.phase[i] = phase_ant_array * 180./np.pi #put into degrees
                self.ants[i] = ant_names
                self.time[i] = times
                self.flags[i] = flags_ant_array
                
            else:
                logger.info('Filling with NaNs. Gain table not present for B{}'.format(beam))
                self.amp[i] = np.full((12,2,2),np.nan)
                self.phase[i] = np.full((12,2,2),np.nan)
                self.ants[i] = ['RT2','RT3','RT4','RT5','RT6','RT7','RT8','RT9','RTA','RTB','RTC','RTD']
                self.time[i] = np.full((2),np.nan)
                self.flags[i] = np.full((12,2,2),np.nan)
            
    def plot_amp(self, imagepath=None):
        """Plot amplitude, one plot per antenna"""

        logger.info("Creating plots for gain amplitude")

        imagepath = self.create_imagepath(imagepath)

        #put plots in default place w/ default name
        ant_names = self.ants[0]
        #figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        for a,ant in enumerate(ant_names):
            #iterate through antennas
            #set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx*4
            ysize = ny*4
            plt.figure(figsize=(xsize,ysize))
            plt.suptitle('Gain amplitude for Antenna {0}'.format(ant),size=30)
            
            for n,beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(self.time[n],self.amp[n][a,:,0],
                           label='XX',
                           marker=',',s=5)
                plt.scatter(self.time[n],self.amp[n][a,:,1],
                           label='YY',
                           marker=',',s=5)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(10,30)
            plt.legend(markerscale=3,fontsize=14)
            plt.savefig(plt.savefig('{imagepath}/Gain_amp_{ant}_{scan}.png'.format(ant=ant,scan=self.scan,imagepath=imagepath)))
            #plt.clf()
            # to really close the plot, this will do
            plt.close('all')
            
    def plot_phase(self,imagepath=None):
        """Plot phase, one plot per antenna"""

        logger.info("Creating plots for gain phase")

        imagepath = self.create_imagepath(imagepath)

        #put plots in default place w/ default name
        ant_names = self.ants[0]
        #figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        for a,ant in enumerate(ant_names):
            #iterate through antennas
            #set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx*4
            ysize = ny*4
            plt.figure(figsize=(xsize,ysize))
            plt.suptitle('Gain phase for Antenna {0}'.format(ant),size=30)
            
            for n,beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(self.time[n],self.phase[n][a,:,0],
                           label='XX',marker=',',s=5)
                plt.scatter(self.time[n],self.phase[n][a,:,1],
                           label='YY',marker=',',s=5)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(-180,180)
            plt.legend(markerscale=3,fontsize=14)
            plt.savefig(plt.savefig('{2}/Gain_phase_{0}_{1}.png'.format(ant,self.scan,imagepath)))
            #plt.clf()
            # to really close the plot, this will do
            plt.close('all')


class GDSols(ScanData):
    def __init__(self, scan, fluxcal, trigger_mode):
        ScanData.__init__(self, scan, fluxcal, trigger_mode=trigger_mode)
        self.imagepathsuffix = "crosscal"
        self.ants = np.empty(len(self.dirlist),dtype=np.object)
        self.delays = np.empty(len(self.dirlist),dtype=np.ndarray)

    def get_data(self):
        # get the data
        for i, (path, beam) in enumerate(zip(self.dirlist, self.beamlist)):
            gdtable = "{0}/raw/{1}.K".format(path, self.sourcename)
            if os.path.isdir(gdtable):
                taql_command = ("SELECT FPARAM FROM {0} ").format(gdtable)
                t = pt.taql(taql_command)
                delays = t.getcol('FPARAM')
                taql_antnames = "SELECT NAME FROM {0}::ANTENNA".format(gdtable)
                t = pt.taql(taql_antnames)
                ant_names = t.getcol("NAME")

                self.ants[i] = ant_names
                self.delays[i] = delays[:,0,:]

            else:
                logger.info('Filling with NaNs. Global delay table not present for B{}'.format(beam))
                self.ants[i] = misc.create_antnames()
                self.delays[i] = np.full((12, 2), np.nan)

    def plot_delay(self, imagepath=None):
        """Plot amplitude, one plot per antenna"""

        logger.info("Creating plots for global delay")

        imagepath = self.create_imagepath(imagepath)

        # put plots in default place w/ default name
        ant_names = self.ants[0]
        # figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        # set up for 8x5 plots (40 beams)
        nx = 8
        ny = 5
        xsize = nx * 4
        ysize = ny * 4
        plt.figure(figsize=(xsize, ysize))
        plt.suptitle('Global delay', size=30)

        for n, beam in enumerate(self.beamlist):
            beamnum = int(beam)
            plt.subplot(ny, nx, beamnum + 1)
            plt.scatter(self.ants[n], self.delays[n][:,0], label='X', marker='o', s=5)
            plt.scatter(self.ants[n], self.delays[n][:,1], label='Y', marker='o', s=5)
            plt.title('Beam {0}'.format(beam))
        plt.legend(markerscale=3, fontsize=14)
        plt.savefig(plt.savefig('{imagepath}/K_{scan}.png'.format(scan=self.scan, imagepath=imagepath)))
        # to really close the plot, this will do
        plt.close('all')


    def plot_dish_delay(self, imagepath=None):
        """Plot global delays, dish-based views"""

        logger.info("Creating dish-based plots for global delay")

        imagepath = self.create_imagepath(imagepath)

        # put plots in default place w/ default name
        ant_names = self.ants[0]
        # figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        # set up for 4x3 plots (12 dishes)
        nx = 4
        ny = 3
        xsize = nx * 4
        ysize = ny * 4
        plt.figure(figsize=(xsize, ysize))
        plt.suptitle('Global dish-based delay', size=30)

        #reshape array
        delays = np.hstack(self.delays).reshape((12,40,2))
        beamarray = np.arange(len(self.beamlist))

        for n, ant in enumerate(ant_names):
            plt.subplot(ny, nx, n + 1)
            plt.scatter(beamarray, delays[n,:,0], label='X', marker='o', s=5)
            plt.scatter(beamarray, delays[n,:,1], label='Y', marker='o', s=5)
            plt.title('Dish {0}'.format(ant))
        plt.legend(markerscale=3, fontsize=14)
        plt.xlabel('beam number')
        plt.ylabel('Delay, nanoseconds')
        plt.savefig(plt.savefig('{imagepath}/K_dish_{scan}.png'.format(scan=self.scan, imagepath=imagepath)))
        # to really close the plot, this will do
        plt.close('all')


class LeakSols(ScanData):
    def __init__(self, scan, fluxcal, trigger_mode):
        ScanData.__init__(self, scan, fluxcal, trigger_mode=trigger_mode)
        self.imagepathsuffix = "crosscal"
        self.ants = np.empty(len(self.dirlist),dtype=np.object)
        self.freq = np.empty(len(self.dirlist),dtype=np.ndarray)
        self.flags = np.empty(len(self.dirlist),dtype=np.ndarray)
        self.leakage = np.empty((len(self.dirlist)),dtype=np.ndarray)

    def get_data(self):
        # get the data
        for i, (path, beam) in enumerate(zip(self.dirlist, self.beamlist)):
            leaktable = "{0}/raw/{1}.Df".format(path, self.sourcename)
            if os.path.isdir(leaktable):
                taql_command = ("SELECT abs(CPARAM) AS amp, arg(CPARAM) AS phase, FLAG FROM {0}").format(leaktable)
                t = pt.taql(taql_command)
                ampleak_sols=t.getcol('amp')
                phaseleak_sols = t.getcol('phase')
                flags = t.getcol('FLAG')
                taql_antnames = "SELECT NAME FROM {0}::ANTENNA".format(leaktable)
                t = pt.taql(taql_antnames)
                ant_names = t.getcol("NAME")
                taql_freq = "SELECT CHAN_FREQ FROM {0}::SPECTRAL_WINDOW".format(leaktable)
                t = pt.taql(taql_freq)
                freqs = t.getcol('CHAN_FREQ')

                # check for flags and mask
                ampleak_sols[flags] = np.nan
                phaseleak_sols[flags] = np.nan

                self.ants[i] = ant_names
                self.phase[i] = phaseleak_sols *180./np.pi #put into degrees
                self.amp[i] = ampleak_sols
                self.flags[i] = flags
                self.freq[i] = freqs

            else:
                logger.info('Filling with NaNs. Polarisation leakage table not present for B{}'.format(beam))
                self.ants[i] = misc.create_antnames()
                self.phase[i] = np.full((12, 2, 2),np.nan)
                self.amp[i] = np.full((12, 2, 2), np.nan)
                self.freq[i] = np.full((2, 2), np.nan)

    def plot_amp(self, imagepath=None):
        """Plot leakage, one plot per antenna"""

        logger.info("Creating plots for amplitude leakage")
        imagepath = self.create_imagepath(imagepath)
        # put plots in default place w/ default name
        ant_names = self.ants[0]
        for a, ant in enumerate(ant_names):
            # iterate through antennas
            # set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx * 4
            ysize = ny * 4
            plt.figure(figsize=(xsize, ysize))
            plt.suptitle('Amplitude polarisation leakage for Antenna {0}'.format(ant), size=30)

            for n, beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum + 1)
                plt.scatter(self.freq[n][0, :], self.amp[n][a, :, 0], label='X', marker=',', s=1)
                plt.scatter(self.freq[n][0, :], self.amp[n][a, :, 1], label='Y', marker=',', s=1)
                plt.title('Beam {0}'.format(beam))
            plt.legend(markerscale=3, fontsize=14)
            plt.savefig('{imagepath}/Df_amp_{ant}_{scan}.png'.format(ant=ant, scan=self.scan, imagepath=imagepath))
            # to really close the plot, this will do
            plt.close('all')

    def plot_phase(self, imagepath=None):
        """Plot leakage, one plot per antenna"""

        logger.info("Creating plots for phase leakage")
        imagepath = self.create_imagepath(imagepath)
        # put plots in default place w/ default name
        ant_names = self.ants[0]
        for a, ant in enumerate(ant_names):
            # iterate through antennas
            # set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx * 4
            ysize = ny * 4
            plt.figure(figsize=(xsize, ysize))
            plt.suptitle('Phase polarisation leakage for Antenna {0}'.format(ant), size=30)

            for n, beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum + 1)
                plt.scatter(self.freq[n][0, :], self.phase[n][a, :, 0], label='X', marker=',', s=1)
                plt.scatter(self.freq[n][0, :], self.phase[n][a, :, 1], label='Y', marker=',', s=1)
                plt.title('Beam {0}'.format(beam))
            plt.legend(markerscale=3, fontsize=14)
            plt.savefig('{imagepath}/Df_phase_{ant}_{scan}.png'.format(ant=ant, scan=self.scan, imagepath=imagepath))
            # to really close the plot, this will do
            plt.close('all')


class KCrossSols(ScanData):
    def __init__(self, scan, polcal, trigger_mode):
        ScanData.__init__(self, scan, polcal, trigger_mode=trigger_mode)
        self.imagepathsuffix = "crosscal"
        self.ants = np.empty(len(self.dirlist),dtype=np.object)
        self.delays = np.empty(len(self.dirlist),dtype=np.ndarray)

    def get_data(self):
        # get the data
        for i, (path, beam) in enumerate(zip(self.dirlist, self.beamlist)):
            gdtable = "{0}/raw/{1}.Kcross".format(path, self.sourcename)
            if os.path.isdir(gdtable):
                taql_command = ("SELECT FPARAM FROM {0} ").format(gdtable)
                t = pt.taql(taql_command)
                delays = t.getcol('FPARAM')
                taql_antnames = "SELECT NAME FROM {0}::ANTENNA".format(gdtable)
                t = pt.taql(taql_antnames)
                ant_names = t.getcol("NAME")

                self.ants[i] = ant_names
                self.delays[i] = delays[:,0,:]

            else:
                logger.info('Filling with NaNs. Cross hand delay table not present for B{}'.format(beam))
                self.ants[i] = misc.create_antnames()
                self.delays[i] = np.full((12, 2), np.nan)

    def plot_delay(self, imagepath=None):
        """Plot amplitude, one plot per antenna"""

        logger.info("Creating plots for cross hand delay")

        imagepath = self.create_imagepath(imagepath)

        # put plots in default place w/ default name
        ant_names = self.ants[0]
        # figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        # set up for 8x5 plots (40 beams)
        nx = 8
        ny = 5
        xsize = nx * 4
        ysize = ny * 4
        plt.figure(figsize=(xsize, ysize))
        plt.suptitle('Cross hand delay', size=30)

        for n, beam in enumerate(self.beamlist):
            beamnum = int(beam)
            plt.subplot(ny, nx, beamnum + 1)
            plt.scatter(self.ants[n], self.delays[n][:,0], label='X', marker='o', s=5)
            plt.scatter(self.ants[n], self.delays[n][:,1], label='Y', marker='o', s=5)
            plt.title('Beam {0}'.format(beam))
        plt.legend(markerscale=3, fontsize=14)
        plt.savefig(plt.savefig('{imagepath}/Kcross_{scan}.png'.format(scan=self.scan, imagepath=imagepath)))
        # to really close the plot, this will do
        plt.close('all')


class PolangleSols(ScanData):
    def __init__(self, scan, polcal, trigger_mode):
        ScanData.__init__(self, scan, polcal, trigger_mode=trigger_mode)
        self.imagepathsuffix = "crosscal"
        self.ants = np.empty(len(self.dirlist),dtype=np.object)
        self.freq = np.empty(len(self.dirlist),dtype=np.ndarray)
        self.flags = np.empty(len(self.dirlist),dtype=np.ndarray)
        self.polangle = np.empty((len(self.dirlist)),dtype=np.ndarray)

    def get_data(self):
        # get the data
        for i, (path, beam) in enumerate(zip(self.dirlist, self.beamlist)):
            polangletable = "{0}/raw/{1}.Xf".format(path, self.sourcename)
            if os.path.isdir(polangletable):
                taql_command = ("SELECT abs(CPARAM) AS amp, arg(CPARAM) AS phase, FLAG FROM {0}").format(polangletable)
                t = pt.taql(taql_command)
                amppolangle_sols=t.getcol('amp')
                phasepolangle_sols = t.getcol('phase')
                flags = t.getcol('FLAG')
                taql_antnames = "SELECT NAME FROM {0}::ANTENNA".format(polangletable)
                t = pt.taql(taql_antnames)
                ant_names = t.getcol("NAME")
                taql_freq = "SELECT CHAN_FREQ FROM {0}::SPECTRAL_WINDOW".format(polangletable)
                t = pt.taql(taql_freq)
                freqs = t.getcol('CHAN_FREQ')

                # check for flags and mask
                amppolangle_sols[flags] = np.nan
                phasepolangle_sols[flags] = np.nan

                self.ants[i] = ant_names
                self.phase[i] = phasepolangle_sols *180./np.pi #put into degrees
                self.amp[i] = amppolangle_sols
                self.flags[i] = flags
                self.freq[i] = freqs

            else:
                logger.info('Filling with NaNs. Polarisation angle table not present for B{}'.format(beam))
                self.ants[i] = misc.create_antnames()
                self.phase[i] = np.full((12, 2, 2),np.nan)
                self.amp[i] = np.full((12, 2, 2), np.nan)
                self.freq[i] = np.full((2, 2), np.nan)

    def plot_amp(self, imagepath=None):
        """Plot leakage, one plot per antenna"""

        logger.info("Creating plots for amplitude polarisation angle corrections")
        imagepath = self.create_imagepath(imagepath)
        # put plots in default place w/ default name
        ant_names = self.ants[0]
        for a, ant in enumerate(ant_names):
            # iterate through antennas
            # set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx * 4
            ysize = ny * 4
            plt.figure(figsize=(xsize, ysize))
            plt.suptitle('Amplitude polarisation angle for Antenna {0}'.format(ant), size=30)

            for n, beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum + 1)
                plt.scatter(self.freq[n][0, :], self.amp[n][a, :, 0], marker=',', s=1)
                plt.title('Beam {0}'.format(beam))
            plt.savefig('{imagepath}/Xf_amp_{ant}_{scan}.png'.format(ant=ant, scan=self.scan, imagepath=imagepath))
            # to really close the plot, this will do
            plt.close('all')

    def plot_phase(self, imagepath=None):
        """Plot leakage, one plot per antenna"""

        logger.info("Creating plots for phase polarisation angle corrections")
        imagepath = self.create_imagepath(imagepath)
        # put plots in default place w/ default name
        ant_names = self.ants[0]
        for a, ant in enumerate(ant_names):
            # iterate through antennas
            # set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx * 4
            ysize = ny * 4
            plt.figure(figsize=(xsize, ysize))
            plt.suptitle('Phase polarisation angle for Antenna {0}'.format(ant), size=30)

            for n, beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum + 1)
                plt.scatter(self.freq[n][0, :], self.phase[n][a, :, 0], marker=',', s=1)
                plt.title('Beam {0}'.format(beam))
            plt.savefig('{imagepath}/Xf_phase_{ant}_{scan}.png'.format(ant=ant, scan=self.scan, imagepath=imagepath))
            # to really close the plot, this will do
            plt.close('all')


class ModelData(ScanData):
    def __init__(self,scan,fluxcal,trigger_mode):
        ScanData.__init__(self,scan,fluxcal,trigger_mode=trigger_mode)
        self.imagepathsuffix = "crosscal"
        self.freq = np.empty(len(self.dirlist),dtype=np.ndarray)
        
    def get_data(self):
        for i, (path,beam) in enumerate(zip(self.dirlist,self.beamlist)):
            msfile = "{0}/raw/{1}.MS".format(path,self.sourcename)
            taql_freq = "SELECT CHAN_FREQ FROM {0}::SPECTRAL_WINDOW".format(msfile)
            t = pt.taql(taql_freq)
            freqs = t.getcol('CHAN_FREQ')[0,:]
            try:
                taql_command = "SELECT abs(gmeans(MODEL_DATA)) AS amp, arg(gmeans(MODEL_DATA)) AS phase FROM {0}".format(msfile)
                t = pt.taql(taql_command)
                amp = t.getcol('amp')[0,:,:]
                phase = t.getcol('phase')[0,:,:]
            except:
                amp = np.empty((len(freqs),4),np.nan)
                phase = np.empty((len(freqs),4),np.nan)
            
            self.amp[i] = amp
            self.phase[i] = phase
            self.freq[i] = freqs
            
    def plot_amp(self,imagepath=None):
        """Plot amplitude, one subplot per beam"""

        logger.info("Creating plots for model amplitude")

        imagepath = self.create_imagepath(imagepath)
        #put plots in default place w/ default name
        nx = 8
        ny = 5
        xsize = nx*4
        ysize = ny*4
        plt.figure(figsize=(xsize,ysize))           
        plt.suptitle('Model amplitude')
            
        for n,beam in enumerate(self.beamlist):
            beamnum = int(beam)
            plt.subplot(ny, nx, beamnum+1)
            plt.plot(self.freq[n],self.amp[n][:,0],
                     label='XX')
            plt.plot(self.freq[n],self.amp[n][:,3],
                     label='YY')
            plt.title('Beam {0}'.format(beam))
            #plt.ylim(10,30)
        plt.legend(markerscale=3,fontsize=14)
        plt.savefig(plt.savefig('{1}/Model_amp_{0}.png'.format(self.scan,imagepath)))
        #plt.clf()
        # to really close the plot, this will do
        plt.close('all')
            
    def plot_phase(self,imagepath=None):
        """Plot amplitude, one subplot per beam"""

        logger.info("Creating plots for model phase")

        imagepath = self.create_imagepath(imagepath)
        #put plots in default place w/ default name
        nx = 8
        ny = 5
        xsize = nx*4
        ysize = ny*4
        plt.figure(figsize=(xsize,ysize))           
        plt.suptitle('Model phase',size=30)
            
        for n,beam in enumerate(self.beamlist):
            beamnum = int(beam)
            plt.subplot(ny, nx, beamnum+1)
            plt.plot(self.freq[n],self.phase[n][:,0],
                     label='XX')
            plt.plot(self.freq[n],self.phase[n][:,3],
                     label='YY')
            plt.title('Beam {0}'.format(beam))
            #plt.ylim(10,30)
        plt.legend(markerscale=3,fontsize=14)
        plt.savefig(plt.savefig('{1}/Model_phase_{0}.png'.format(self.scan,imagepath)))
        #plt.clf()
        # to really close the plot, this will do
        plt.close('all')


class AutocorrData(ScanData):
    def __init__(self, scan, fluxcal, trigger_mode):
        ScanData.__init__(self, scan, fluxcal, trigger_mode=trigger_mode)
        self.imagepathsuffix = "crosscal"
        self.freq = np.empty(len(self.dirlist), dtype=np.ndarray)
        self.ants = np.empty(len(self.dirlist), dtype=np.object)

    def get_data(self):
        for i, (path, beam) in enumerate(zip(self.dirlist, self.beamlist)):
            msfile = "{0}/raw/{1}.MS".format(path, self.sourcename)
            taql_antnames = "SELECT NAME FROM {0}::ANTENNA".format(msfile)
            t = pt.taql(taql_antnames)
            ant_names = t.getcol("NAME")

            #then get frequencies:
            taql_freq = "SELECT CHAN_FREQ FROM {0}::SPECTRAL_WINDOW".format(
                msfile)
            t = pt.taql(taql_freq)
            freqs = t.getcol('CHAN_FREQ')[0, :]

            #and number of stokes params
            taql_stokes = "SELECT abs(DATA) AS amp from {0} limit 1" .format(
                msfile)
            t_pol = pt.taql(taql_stokes)
            pol_array = t_pol.getcol('amp')
            n_stokes = pol_array.shape[2]  # shape is time, one, nstokes

            #take MS file and get calibrated data
            amp_ant_array = np.empty(
                (len(ant_names), len(freqs), n_stokes), dtype=object)
            # phase_ant_array = np.empty(
            #     (len(ant_names), len(freqs), n_stokes), dtype=object)

            for ant in xrange(len(ant_names)):
                try:
                    taql_command = ("SELECT abs(gmeans(CORRECTED_DATA[FLAG])) AS amp "
                                    "FROM {0} "
                                    "WHERE ANTENNA1==ANTENNA2 && (ANTENNA1={1} || ANTENNA2={1})").format(msfile, ant)
                    t = pt.taql(taql_command)
                    test = t.getcol('amp')
                    amp_ant_array[ant, :, :] = t.getcol('amp')[0, :, :]
                    #phase_ant_array[ant, :, :] = t.getcol('phase')[0, :, :]
                except Exception as e:
                    amp_ant_array[ant, :, :] = np.full(
                        (len(freqs), n_stokes), np.nan)
                    # phase_ant_array[ant, :, :] = np.full(
                    #     (len(freqs), n_stokes), np.nan)
                    logger.exception(e)

            #self.phase[i] = phase_ant_array
            self.amp[i] = amp_ant_array
            self.freq[i] = freqs
            self.ants[i] = ant_names

    def plot_autocorr_per_antenna(self, imagepath=None):
        """
        Plot the autocorrelation for each antenna for all beams
        """

        logger.info("Creating plots for autocorrelation plots per antenna")

        #first define imagepath if not given by user
        imagepath = self.create_imagepath(imagepath)

        #plot amplitude, one plot per antenna
        #put plots in default place w/ default name
        ant_names = self.ants[0]
        #figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        for a, ant in enumerate(ant_names):
            #iterate through antennas
            #set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx*4
            ysize = ny*4
            plt.figure(figsize=(xsize, ysize))
            plt.suptitle(
                'Autocorrelation of Antenna {0}'.format(ant), size=30)

            for n, beam in enumerate(self.beamlist):
                freq = self.freq[n]
                amp_xx = self.amp[n][a, :, 0]
                amp_yy = self.amp[n][a, :, 3]
                logger.debug(np.min(amp_xx))
                logger.debug(np.max(amp_xx))
                logger.debug(np.min(amp_xx[np.where(amp_xx != 0.)[0]]))
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(freq[np.where(amp_xx != 0.)[0]], amp_xx[np.where(amp_xx != 0.)[0]],
                            label='XX',
                            marker=',', s=1)
                plt.scatter(freq[np.where(amp_yy != 0.)[0]], amp_yy[np.where(amp_yy != 0)[0]],
                            label='YY',
                            marker=',', s=1)
                # plt.scatter(self.freq[n][np.where(self.amp[n][a, :, 0] != 0)[0]], self.amp[n][a, :, 0][np.where(self.amp[n][a, :, 0] != 0)[0]],
                #             label='XX',
                #             marker=',', s=1)
                # plt.scatter(self.freq[n][np.where(self.amp[n][a, :, 0] != 0)[0]], self.amp[n][a, :, 3][np.where(self.amp[n][a, :, 0] != 0)[0]],
                #             label='YY',
                #             marker=',', s=1)
                plt.title('Beam {0}'.format(beam))
                #plt.ylim(0, 30)
            plt.legend(markerscale=3, fontsize=14)
            plt.savefig(plt.savefig(
                '{2}/Autocorrelation_Antenna_{0}_{1}.png'.format(ant, self.scan, imagepath)))
            #plt.clf()
            # to really close the plot, this will do
            plt.close('all')

    def plot_autocorr_per_beam(self, imagepath=None):
        """
        Plot the autocorrelation for each beam with all antennas
        """

        logger.info("Creating plots for autocorrelation plots per beam")

        #first define imagepath if not given by user
        imagepath = self.create_imagepath(imagepath)

        #plot amplitude, one plot per antenna
        #put plots in default place w/ default name
        ant_names = self.ants[0]
        #figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        for n, beam in enumerate(self.beamlist):
            beamnum = int(beam)
            #iterate through antennas
            #set up for 8x5 plots (40 beams)
            nx = 4
            ny = 3
            xsize = nx*4
            ysize = ny*4
            plt.figure(figsize=(xsize, ysize))
            plt.suptitle(
                'Autocorrelation of Beam {0:02d}'.format(beamnum), size=30)

            for a, ant in enumerate(ant_names):
            
                plt.subplot(ny, nx, a+1)
                plt.scatter(self.freq[n], self.amp[n][a, :, 0],
                            label='XX',
                            marker=',', s=1)
                plt.scatter(self.freq[n], self.amp[n][a, :, 3],
                            label='YY',
                            marker=',', s=1)
                plt.title('Antenna {0}'.format(ant))
                #plt.ylim(0, 30)
            plt.legend(markerscale=3, fontsize=14)
            plt.savefig(plt.savefig(
                '{2}/Autocorrelation_Beam_{0:02d}_{1}.png'.format(beamnum, self.scan, imagepath)))
            #plt.clf()
            # to really close the plot, this will do
            plt.close('all')
       
class CorrectedData(ScanData):
    def __init__(self,scan,fluxcal,trigger_mode):
        ScanData.__init__(self,scan,fluxcal,trigger_mode=trigger_mode)
        self.imagepathsuffix = "crosscal"
        self.freq = np.empty(len(self.dirlist),dtype=np.ndarray)
        self.ants = np.empty(len(self.dirlist),dtype=np.object)
        
    def get_data(self):
        for i, (path,beam) in enumerate(zip(self.dirlist,self.beamlist)):
            msfile = "{0}/raw/{1}.MS".format(path,self.sourcename)
            taql_antnames = "SELECT NAME FROM {0}::ANTENNA".format(msfile)
            t= pt.taql(taql_antnames)
            ant_names=t.getcol("NAME")

            #then get frequencies:
            taql_freq = "SELECT CHAN_FREQ FROM {0}::SPECTRAL_WINDOW".format(msfile)
            t = pt.taql(taql_freq)
            freqs = t.getcol('CHAN_FREQ')[0,:]
    
            #and number of stokes params
            taql_stokes = "SELECT abs(DATA) AS amp from {0} limit 1" .format(msfile)
            t_pol = pt.taql(taql_stokes)
            pol_array = t_pol.getcol('amp')
            n_stokes = pol_array.shape[2] #shape is time, one, nstokes
    
            #take MS file and get calibrated data
            amp_ant_array = np.empty((len(ant_names),len(freqs),n_stokes),dtype=object)
            phase_ant_array = np.empty((len(ant_names),len(freqs),n_stokes),dtype=object)
    
            for ant in xrange(len(ant_names)):
                try:
                    taql_command = ("SELECT abs(gmeans(CORRECTED_DATA[FLAG])) AS amp, "
                                    "arg(gmeans(CORRECTED_DATA[FLAG])) AS phase FROM {0} "
                                    "WHERE ANTENNA1!=ANTENNA2 && "
                                    "(ANTENNA1={1} || ANTENNA2={1})").format(msfile,ant)
                    t = pt.taql(taql_command)
                    test=t.getcol('amp')
                    amp_ant_array[ant,:,:] = t.getcol('amp')[0,:,:]
                    phase_ant_array[ant,:,:] = t.getcol('phase')[0,:,:]
                except:
                    amp_ant_array[ant,:,:] = np.full((len(freqs),n_stokes),np.nan)
                    phase_ant_array[ant,:,:] = np.full((len(freqs),n_stokes),np.nan)
                
            self.phase[i] = phase_ant_array
            self.amp[i] = amp_ant_array
            self.freq[i] = freqs
            self.ants[i] = ant_names
            
    def plot_amp(self,imagepath=None):

        logger.info("Creating plots for corrected amplitude")

        #first define imagepath if not given by user
        imagepath = self.create_imagepath(imagepath)

        #plot amplitude, one plot per antenna
        #put plots in default place w/ default name
        ant_names = self.ants[0]
        #figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        for a,ant in enumerate(ant_names):
            #iterate through antennas
            #set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx*4
            ysize = ny*4
            plt.figure(figsize=(xsize,ysize))
            plt.suptitle('Corrected amplitude for Antenna {0} (baselines averaged)'.format(ant),size=30)
            
            for n,beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(self.freq[n],self.amp[n][a,:,0],
                           label='XX',
                           marker=',',s=1)
                plt.scatter(self.freq[n],self.amp[n][a,:,3],
                           label='YY',
                           marker=',',s=1)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(0,30)
            plt.legend(markerscale=3,fontsize=14)
            plt.savefig(plt.savefig('{2}/Corrected_amp_{0}_{1}.png'.format(ant,self.scan,imagepath)))
            #plt.clf()
            # to really close the plot, this will do
            plt.close('all')
            
    def plot_phase(self,imagepath=None):

        logger.info("Creating plots for corrected phase")

        #plot amplitude, one plot per antenna
        imagepath = self.create_imagepath(imagepath)
        #put plots in default place w/ default name
        ant_names = self.ants[0]
        #figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        for a,ant in enumerate(ant_names):
            #iterate through antennas
            #set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx*4
            ysize = ny*4
            plt.figure(figsize=(xsize,ysize))
            plt.suptitle('Corrected phase for Antenna {0} (baselines averaged)'.format(ant))
            
            for n,beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(self.freq[n],self.phase[n][a,:,0],
                           label='XX',
                           marker=',',s=1)
                plt.scatter(self.freq[n],self.phase[n][a,:,3],
                           label='YY',
                           marker=',',s=1)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(-3,3)
            plt.legend(markerscale=3,fontsize=14)
            plt.savefig(plt.savefig('{2}/Corrected_phase_{0}_{1}.png'.format(ant,self.scan,imagepath)))
            #plt.clf()
            # to really close the plot, this will do
            plt.close('all')


class RawData(ScanData):
    def __init__(self,scan,fluxcal,trigger_mode):
        ScanData.__init__(self,scan,fluxcal,trigger_mode=trigger_mode)
        self.imagepathsuffix = "crosscal"
        self.freq = np.empty(len(self.dirlist),dtype=np.ndarray)
        self.ants = np.empty(len(self.dirlist),dtype=np.object)
        
    def get_data(self):
        for i, (path,beam) in enumerate(zip(self.dirlist,self.beamlist)):
            msfile = "{0}/raw/{1}.MS".format(path,self.sourcename)
            taql_antnames = "SELECT NAME FROM {0}::ANTENNA".format(msfile)
            t= pt.taql(taql_antnames)
            ant_names=t.getcol("NAME")

            #then get frequencies:
            taql_freq = "SELECT CHAN_FREQ FROM {0}::SPECTRAL_WINDOW".format(msfile)
            t = pt.taql(taql_freq)
            freqs = t.getcol('CHAN_FREQ')[0,:]
    
            #and number of stokes params
            taql_stokes = "SELECT abs(DATA) AS amp from {0} limit 1" .format(msfile)
            t_pol = pt.taql(taql_stokes)
            pol_array = t_pol.getcol('amp')
            n_stokes = pol_array.shape[2] #shape is time, one, nstokes
    
            #take MS file and get calibrated data
            amp_ant_array = np.empty((len(ant_names),len(freqs),n_stokes),dtype=object)
            phase_ant_array = np.empty((len(ant_names),len(freqs),n_stokes),dtype=object)
    
            for ant in xrange(len(ant_names)):
                try:
                    taql_command = ("SELECT abs(gmeans(DATA[FLAG])) AS amp, "
                                    "arg(gmeans(DATA[FLAG])) AS phase FROM {0} "
                                    "WHERE ANTENNA1!=ANTENNA2 && "
                                    "(ANTENNA1={1} || ANTENNA2={1})").format(msfile,ant)
                    t = pt.taql(taql_command)
                    test=t.getcol('amp')
                    amp_ant_array[ant,:,:] = t.getcol('amp')[0,:,:]
                    phase_ant_array[ant,:,:] = t.getcol('phase')[0,:,:]
                except:
                    amp_ant_array[ant,:,:] = np.full((len(freqs),n_stokes),np.nan) #t.getcol('amp')[0,:,:]
                    phase_ant_array[ant,:,:] = np.full((len(freqs),n_stokes),np.nan) #t.getcol('phase')[0,:,:]
                
            self.phase[i] = phase_ant_array
            self.amp[i] = amp_ant_array
            self.freq[i] = freqs
            self.ants[i] = ant_names
            
    def plot_amp(self,imagepath=None):
        logger.info("Creating plots for raw amplitude")

        #plot amplitude, one plot per antenna
        imagepath = self.create_imagepath(imagepath)
        #put plots in default place w/ default name
        ant_names = self.ants[0]
        #figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        for a,ant in enumerate(ant_names):
            #iterate through antennas
            #set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx*4
            ysize = ny*4
            plt.figure(figsize=(xsize,ysize))
            plt.suptitle('Raw amplitude for Antenna {0} (baselines averaged)'.format(ant),size=30)
            
            for n,beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(self.freq[n],self.amp[n][a,:,0],
                           label='XX',
                           marker=',',s=1)
                plt.scatter(self.freq[n],self.amp[n][a,:,3],
                           label='YY',
                           marker=',',s=1)
                plt.title('Beam {0}'.format(beam))
                #plt.ylim(10,30)
            plt.legend(markerscale=3,fontsize=14)
            plt.savefig(plt.savefig('{2}/Raw_amp_{0}_{1}.png'.format(ant,self.scan,imagepath)))
            #plt.clf()
            # to really close the plot, this will do
            plt.close('all')
            
    def plot_phase(self,imagepath=None):

        logger.info("Creating plots for raw phase")

        #plot amplitude, one plot per antenna
        imagepath = self.create_imagepath(imagepath)

        #put plots in default place w/ default name
        ant_names = self.ants[0]
        #figlist = ['fig_'+str(i) for i in range(len(ant_names))]
        for a,ant in enumerate(ant_names):
            #iterate through antennas
            #set up for 8x5 plots (40 beams)
            nx = 8
            ny = 5
            xsize = nx*4
            ysize = ny*4
            plt.figure(figsize=(xsize,ysize))
            plt.suptitle('Raw phase for Antenna {0} (baselines averaged)'.format(ant),size=30)
            
            for n,beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(self.freq[n],self.phase[n][a,:,0],
                           label='XX',
                           marker=',',s=1)
                plt.scatter(self.freq[n],self.phase[n][a,:,3],
                           label='YY',
                           marker=',',s=1)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(-180,180)
            plt.legend(markerscale=3,fontsize=14)
            plt.savefig(plt.savefig('{2}/Raw_phase_{0}_{1}.png'.format(ant,self.scan,imagepath)))
            #plt.clf()
            # to really close the plot, this will do
            plt.close('all')

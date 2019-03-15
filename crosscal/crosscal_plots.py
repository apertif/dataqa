#python "module" for QA plots for cross-cal
#Will want to plot calibration solutions
#also potential for raw and corrected data

#load necessary packages
import os
import numpy as np
from astropy.io import ascii
import apercal
import casacore.tables as pt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ..scandata import ScanData

def make_all_ccal_plots(scan, output_path):
    # Get BP plots
    BP = BPSols(scan, fluxcal)
    BP.get_data()
    BP.plot_amp(imagepath=output_path)
    BP.plot_phase(imagepath=output_path)
    print 'Done with bandpass plots'

    # Get Gain plots
    Gain = GainSols(scan, fluxcal)
    Gain.get_data()
    Gain.plot_amp(imagepath=output_path)
    Gain.plot_phase(imagepath=output_path)
    print 'Done with gainplots'

    # Get Raw data
    Raw = RawData(scan, fluxcal)
    Raw.get_data()
    Raw.plot_amp(imagepath=output_path)
    Raw.plot_phase(imagepath=output_path)
    print 'Done with plotting raw data'

    # Get model data
    Model = ModelData(scan, fluxcal)
    Model.get_data()
    Model.plot_amp(imagepath=output_path)
    Model.plot_phase(imagepath=output_path)
    print 'Done with plotting model data'

    # Get corrected data
    Corrected = CorrectedData(scan, fluxcal)
    Corrected.get_data()
    Corrected.plot_amp(imagepath=output_path)
    Corrected.plot_phase(imagepath=output_path)
    print 'Done with plotting corrected data'


class BPSols(ScanData):
    def __init__(self,scan,fluxcal):
        ScanData.__init__(self,scan,fluxcal)
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
            #print bptable
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
                print 'Filling with NaNs. BP table not present for B{}'.format(beam)
                self.ants[i] = ['RT2','RT3','RT4','RT5','RT6','RT7','RT8','RT9','RTA','RTB','RTC','RTD']
                self.time[i] = np.array(np.nan)
                self.phase[i] = np.full((12,2,2),np.nan)
                self.amp[i] = np.full((12,2,2),np.nan)
                self.freq[i] = np.full((2,2),np.nan)
            
    def plot_amp(self, imagepath=None):
        """Plot amplitude, one plot per antenna"""
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
                #print beamnum
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
    def __init__(self,scan,fluxcal):
        ScanData.__init__(self,scan,fluxcal)
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
                print 'Filling with NaNs. Gain table not present for B{}'.format(beam)
                self.amp[i] = np.full((12,2,2),np.nan)
                self.phase[i] = np.full((12,2,2),np.nan)
                self.ants[i] = ['RT2','RT3','RT4','RT5','RT6','RT7','RT8','RT9','RTA','RTB','RTC','RTD']
                self.time[i] = np.full((2),np.nan)
                self.flags[i] = np.full((12,2,2),np.nan)
            
    def plot_amp(self, imagepath=None):
        """Plot amplitude, one plot per antenna"""
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

        
class ModelData(ScanData):
    def __init__(self,scan,fluxcal):
        ScanData.__init__(self,scan,fluxcal)
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
            
        
class CorrectedData(ScanData):
    def __init__(self,scan,fluxcal):
        ScanData.__init__(self,scan,fluxcal)
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
    def __init__(self,scan,fluxcal):
        ScanData.__init__(self,scan,fluxcal)
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

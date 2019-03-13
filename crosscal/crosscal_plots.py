#python "module" for QA plots for cross-cal
#Will want to plot calibration solutions
#also potential for raw and corrected data

#load necessary packages
import os
import numpy as np
from astropy.io import ascii
import apercal
import casacore.tables as pt
import matplotlib.pyplot as plt



  
"""
Define object classes for holding data related to scans
The key thing to specify an object is the scan of the target field
Also need name of fluxcal (for cross-cal solutions)
Want to add functionality for pol-cal for pol solutions (secondary)
This specifies the location of all data, assuming setup of automatic pipeline
(/data/apertif, distributed across happili nodes)
"""

class ScanData(object):
    #Initilailze with source name, scalist and beamlist
    #and place holders for phase and amplitude
    def __init__(self,scan,fluxcal):
        self.scan = scan
        self.fluxcal = fluxcal
        #check if fluxcal is given as 3CXXX.MS or 3CXXX
        #Fix to not include .MS no matter what
        if self.fluxcal[0:2] != '3C':
            print "Fluxcal doesnt' start with 3C - are you sure?"
        elif self.fluxcal[-2:] == 'MS':
            self.fluxcal = self.fluxcal[:-3]
        #also get a directory list and beamlist
        self.dirlist =[]
        self.beamlist=[]
        #first check what happili node on
        #if not happili-01, print a warning and only search locally
        hostname = os.uname()[1]
        if hostname != 'happili-01':
            print 'Not on happili-01, only search local {} for data'.format(hostname)
            path = '/data/apertif/{}'.format(self.scan)
            allfiles = os.listdir(path)
            for f in allfiles:
                full_path = os.path.join(path, f)
                if os.path.isdir(full_path):
                    self.dirlist.append(full_path)
                    #create a list of all directories with full path. 
                    #This should be all beams - there should be no other directories
                    #f is a string, so add to beam list to also track info about beams
                    self.beamlist.append(f)
        else:
            #On happili-01, so search all nodes
            #ignoring happili-05 - may have to fix this eventually
            path ='/data/apertif/{}'.format(self.scan)
            path2 = '/data2/apertif/{}'.format(self.scan)
            path3 = '/data3/apertif/{}'.format(self.scan)
            path4 = '/data4/apertif/{}'.format(self.scan)            
            files01 = os.listdir(path)
            files02 = os.listdir(path2)
            files03 = os.listdir(path3)
            files04 = os.listdir(path4)
            #have to go through one by one - easiest
            for f in files01:
                full_path = os.path.join(path, f)
                if os.path.isdir(full_path):
                    self.dirlist.append(full_path)
                    #also add to beamlist
                    self.beamlist.append(f)
            for f in files02:
                full_path = os.path.join(path2, f)
                if os.path.isdir(full_path):
                    self.dirlist.append(full_path)
                    #also add to beamlist
                    self.beamlist.append(f)
            for f in files03:
                full_path = os.path.join(path3, f)
                if os.path.isdir(full_path):
                    self.dirlist.append(full_path)
                    #also add to beamlist
                    self.beamlist.append(f)
            for f in files04:
                full_path = os.path.join(path4, f)
                if os.path.isdir(full_path):
                    self.dirlist.append(full_path)
                    #also add to beamlist
                    self.beamlist.append(f)        
        #initiatlizae phase & amp arrays - common to all types of 
        self.phase = np.empty(len(self.dirlist),dtype=np.ndarray)
        self.amp = np.empty(len(self.dirlist),dtype=np.ndarray)
        
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
            bptable = "{0}/raw/{1}.Bscan".format(path,self.fluxcal)
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
            
    def plot_amp(self,imagepath=None):
        #first define imagepath if not given by user
        if imagepath == None:
            #write in user's home directory (know that have write access there)
            myusername = os.environ['USER']
            imagepath = '/home/{}/dataqa_plots'.format(myusername)
        #check if imagepath exists, create if necessary
        if not os.path.exists(imagepath):
            print "{} doesn't exist, creating".format(imagepath)
            os.makedirs(imagepath)
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
            plt.suptitle('Bandpass amplitude for Antenna {0}'.format(ant),size=20)
            
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
            plt.legend()
            plt.savefig('{2}/BP_amp_{0}_{1}.png'.format(ant,self.scan,imagepath))
            plt.clf()
            
    def plot_phase(self,imagepath=None):
        #plot phase, one plot per antenna
        #first define imagepath if not given by user
        if imagepath == None:
            #write in user's home directory (know that have write access there)
            myusername = os.environ['USER']
            imagepath = '/home/{}/dataqa_plots'.format(myusername)
        #check if imagepath exists, create if necessary
        if not os.path.exists(imagepath):
            print "{} doesn't exist, creating".format(imagepath)
            os.makedirs(imagepath)
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
            plt.suptitle('Bandpass phases for Antenna {0}'.format(ant))
            
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
            plt.legend()
            plt.savefig('{2}/BP_phase_{0}_{1}.png'.format(ant,self.scan,imagepath))
            plt.clf()
            
            
        
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
            gaintable = "{0}/raw/{1}.G1ap".format(path,self.fluxcal)
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
                self.amp[i] = np.full((12,2,2),np.nan)
                self.phase[i] = np.full((12,2,2),np.nan)
                self.ants[i] = ['RT2','RT3','RT4','RT5','RT6','RT7','RT8','RT9','RTA','RTB','RTC','RTD']
                self.time[i] = np.full((2),np.nan)
                self.flags[i] = np.full((12,2,2),np.nan)
            
    def plot_amp(self,imagepath=None):
        #first define imagepath if not given by user
        if imagepath == None:
            #write in user's home directory (know that have write access there)
            myusername = os.environ['USER']
            imagepath = '/home/{}/dataqa_plots'.format(myusername)
        #check if imagepath exists, create if necessary
        if not os.path.exists(imagepath):
            print "{} doesn't exist, creating".format(imagepath)
            os.makedirs(imagepath)
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
            plt.suptitle('Gain amplitude for Antenna {0}'.format(ant))
            
            for n,beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(self.time[n],self.amp[n][a,:,0],
                           label='XX',
                           marker=',',s=1)
                plt.scatter(self.time[n],self.amp[n][a,:,1],
                           label='YY',
                           marker=',',s=1)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(10,30)
            plt.legend()
            plt.savefig(plt.savefig('{2}/Gain_amp_{0}_{1}.png'.format(ant,self.scan,imagepath)))
            plt.clf()
            
    def plot_phase(self,imagepath=None):
        #first define imagepath if not given by user
        if imagepath == None:
            #write in user's home directory (know that have write access there)
            myusername = os.environ['USER']
            imagepath = '/home/{}/dataqa_plots'.format(myusername)
        #check if imagepath exists, create if necessary
        if not os.path.exists(imagepath):
            print "{} doesn't exist, creating".format(imagepath)
            os.makedirs(imagepath)
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
            plt.suptitle('Gain phase for Antenna {0}'.format(ant))
            
            for n,beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(self.time[n],self.phase[n][a,:,0],
                           label='XX',marker=',',s=1)
                plt.scatter(self.time[n],self.phase[n][a,:,1],
                           label='YY',marker=',',s=1)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(-180,180)
            plt.legend()
            plt.savefig(plt.savefig('{2}/Gain_phase_{0}_{1}.png'.format(ant,self.scan,imagepath)))
            plt.clf()

        
class ModelData(ScanData):
    def __init__(self,scan,fluxcal):
        ScanData.__init__(self,scan,fluxcal)
        self.freq = np.empty(len(self.dirlist),dtype=np.ndarray)
        
    def get_data(self):
        for i, (path,beam) in enumerate(zip(self.dirlist,self.beamlist)):
            msfile = "{0}/raw/{1}.MS".format(path,self.fluxcal)
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
        #first define imagepath if not given by user
        if imagepath == None:
            #write in user's home directory (know that have write access there)
            myusername = os.environ['USER']
            imagepath = '/home/{}/dataqa_plots'.format(myusername)
        #check if imagepath exists, create if necessary
        if not os.path.exists(imagepath):
            print "{} doesn't exist, creating".format(imagepath)
            os.makedirs(imagepath)
        #plot amplitude, one subplot per beam
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
            plt.legend()
            plt.savefig(plt.savefig('{2}/Model_amp_{0}_{1}.png'.format(ant,self.scan,imagepath)))
            plt.clf()
            
    def plot_phase(self,imagepath=None):
        #first define imagepath if not given by user
        if imagepath == None:
            #write in user's home directory (know that have write access there)
            myusername = os.environ['USER']
            imagepath = '/home/{}/dataqa_plots'.format(myusername)
        #check if imagepath exists, create if necessary
        if not os.path.exists(imagepath):
            print "{} doesn't exist, creating".format(imagepath)
            os.makedirs(imagepath)
        #plot amplitude, one subplot per beam
        #put plots in default place w/ default name
        nx = 8
        ny = 5
        xsize = nx*4
        ysize = ny*4
        plt.figure(figsize=(xsize,ysize))           
        plt.suptitle('Model phase')
            
        for n,beam in enumerate(self.beamlist):
            beamnum = int(beam)
            plt.subplot(ny, nx, beamnum+1)
            plt.plot(self.freq[n],self.phase[n][:,0],
                     label='XX')
            plt.plot(self.freq[n],self.phase[n][:,3],
                     label='YY')
            plt.title('Beam {0}'.format(beam))
            #plt.ylim(10,30)
            plt.legend()
            plt.savefig(plt.savefig('{2}/Model_phase_{0}_{1}.png'.format(ant,self.scan,imagepath)))
            plt.clf()
            
        
class CorrectedData(ScanData):
    def __init__(self,scan,fluxcal):
        ScanData.__init__(self,scan,fluxcal)
        self.freq = np.empty(len(scanlist),dtype=np.ndarray)
        self.ants = np.empty(len(scanlist),dtype=np.object)
        
    def get_data(self):
        for i, (path,beam) in enumerate(zip(self.dirlist,self.beamlist)):
            msfile = "{0}/raw/{1}.MS".format(path,self.fluxcal)
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
                    amp_ant_array[ant,:,:] = np.full((0,len(freqs),n_stokes),np.nan)
                    phase_ant_array[ant,:,:] = np.full((0,len(freqs),n_stokes),np.nan)
                
            self.phase[i] = phase_ant_array
            self.amp[i] = amp_ant_array
            self.freq[i] = freqs
            self.ants[i] = ant_names
            
    def plot_amp(self,imagepath=None):
        #first define imagepath if not given by user
        if imagepath == None:
            #write in user's home directory (know that have write access there)
            myusername = os.environ['USER']
            imagepath = '/home/{}/dataqa_plots'.format(myusername)
        #check if imagepath exists, create if necessary
        if not os.path.exists(imagepath):
            print "{} doesn't exist, creating".format(imagepath)
            os.makedirs(imagepath)
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
            plt.suptitle('Corrected amplitude for Antenna {0}'.format(ant))
            
            for n,beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(self.freq[n],self.amp[n][a,:,0],
                           label='XX, {0}'.format(scan),
                           marker=',',s=1)
                plt.scatter(self.freq[n],self.amp[n][a,:,3],
                           label='YY, {0}'.format(scan),
                           marker=',',s=1)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(10,30)
            plt.legend()
            plt.savefig(plt.savefig('{2}/Corrected_amp_{0}_{1}.png'.format(ant,self.scan,imagepath)))
            plt.clf()
            
    def plot_phase(self,imagepath=None):
        #first define imagepath if not given by user
        if imagepath == None:
            #write in user's home directory (know that have write access there)
            myusername = os.environ['USER']
            imagepath = '/home/{}/dataqa_plots'.format(myusername)
        #check if imagepath exists, create if necessary
        if not os.path.exists(imagepath):
            print "{} doesn't exist, creating".format(imagepath)
            os.makedirs(imagepath)
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
            plt.suptitle('Corrected phase for Antenna {0}'.format(ant))
            
            for n,beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(self.freq[n],self.phase[n][a,:,0],
                           label='XX, {0}'.format(scan),
                           marker=',',s=1)
                plt.scatter(self.freq[n],self.phase[n][a,:,3],
                           label='YY, {0}'.format(scan),
                           marker=',',s=1)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(-3,3)
            plt.legend()
            plt.savefig(plt.savefig('{2}/Corrected_amp_{0}_{1}.png'.format(ant,self.scan,imagepath)))
            plt.clf()
                         
class RawData(ScanData):
    def __init__(self,scan,fluxcal):
        ScanData.__init__(self,scan,fluxcal)
        self.freq = np.empty(len(scanlist),dtype=np.ndarray)
        self.ants = np.empty(len(scanlist),dtype=np.object)
        
    def get_data(self):
        for i, (path,beam) in enumerate(zip(self.dirlist,self.beamlist)):
            msfile = "{0}/raw/{1}.MS".format(path,self.fluxcal)
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
                    taql_command = ("SELECT abs(gmeans(RAW_DATA[FLAG])) AS amp, "
                                    "arg(gmeans(RAW_DATA[FLAG])) AS phase FROM {0} "
                                    "WHERE ANTENNA1!=ANTENNA2 && "
                                    "(ANTENNA1={1} || ANTENNA2={1})").format(msfile,ant)
                    t = pt.taql(taql_command)
                    test=t.getcol('amp')
                    amp_ant_array[ant,:,:] = t.getcol('amp')[0,:,:]
                    phase_ant_array[ant,:,:] = t.getcol('phase')[0,:,:]
                except:
                    amp_ant_array[ant,:,:] = np.full((0,len(freqs),n_stokes),np.nan) #t.getcol('amp')[0,:,:]
                    phase_ant_array[ant,:,:] = np.full((0,len(freqs),n_stokes),np.nan) #t.getcol('phase')[0,:,:]
                
            self.phase[i] = phase_ant_array
            self.amp[i] = amp_ant_array
            self.freq[i] = freqs
            self.ants[i] = ant_names
            
    def plot_amp(self,imagepath=None):
        #first define imagepath if not given by user
        if imagepath == None:
            #write in user's home directory (know that have write access there)
            myusername = os.environ['USER']
            imagepath = '/home/{}/dataqa_plots'.format(myusername)
        #check if imagepath exists, create if necessary
        if not os.path.exists(imagepath):
            print "{} doesn't exist, creating".format(imagepath)
            os.makedirs(imagepath)
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
            plt.suptitle('Raw amplitude for Antenna {0}'.format(ant))
            
            for n,beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(self.freq[n],self.amp[n][a,:,0],
                           label='XX, {0}'.format(scan),
                           marker=',',s=1)
                plt.scatter(self.freq[n],self.amp[n][a,:,3],
                           label='YY, {0}'.format(scan),
                           marker=',',s=1)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(10,30)
            plt.legend()
            plt.savefig(plt.savefig('{2}/Raw_amp_{0}_{1}.png'.format(ant,self.scan,imagepath)))
            plt.clf()
            
    def plot_phase(self,imagepath=None):
        #first define imagepath if not given by user
        if imagepath == None:
            #write in user's home directory (know that have write access there)
            myusername = os.environ['USER']
            imagepath = '/home/{}/dataqa_plots'.format(myusername)
        #check if imagepath exists, create if necessary
        if not os.path.exists(imagepath):
            print "{} doesn't exist, creating".format(imagepath)
            os.makedirs(imagepath)
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
            plt.suptitle('Raw phase for Antenna {0}'.format(ant))
            
            for n,beam in enumerate(self.beamlist):
                beamnum = int(beam)
                plt.subplot(ny, nx, beamnum+1)
                plt.scatter(self.freq[n],self.phase[n][a,:,0],
                           label='XX, {0}'.format(scan),
                           marker=',',s=1)
                plt.scatter(self.freq[n],self.phase[n][a,:,3],
                           label='YY, {0}'.format(scan),
                           marker=',',s=1)
                plt.title('Beam {0}'.format(beam))
                plt.ylim(-3,3)
            plt.legend()
            plt.savefig(plt.savefig('{2}/Raw_amp_{0}_{1}.png'.format(ant,self.scan,imagepath)))
            plt.clf()
    




import time

import pygame
import pygame.midi as pm

# packages needed for the parameter-display
from pygame.locals import *
import pygame.font

from numpy import intersect1d, array
import numpy as np

import matplotlib
matplotlib.use('TkAgg') # do this before importing pylab
import matplotlib.pyplot as plt

from Dunkel_pars import parameters
from Dunkel_functions import small2string, neuron2note, linear2grid

global pars
pars = parameters()

class DeviceStruct(dict):
    def __init__(self,name='SimpleSynth virtual input',maxNumSignals=None,
                 updateInterval=1,instrument=1,velocity=64):
        self['name']=name
        self['maxNumSignals']=maxNumSignals
        self['updateInterval']=updateInterval
        self['instrument']=instrument
        self['velocity']=velocity

class OutputDevice(pm.Output):
    def __init__(self,deviceStruct):
        id = self.__getDeviceId(deviceStruct['name'])
        if id == -1:
            print "SETUP Warning: output: "+deviceStruct['name']+ " not available!!!"
            return None
        else:
            super(OutputDevice,self).__init__(id)
            self.__name = deviceStruct['name']
            self.__velocity = deviceStruct['velocity']
            self.set_instrument(deviceStruct['instrument'])
            self.__maxNumSignals = deviceStruct['maxNumSignals']
            self.__updateInterval = deviceStruct['updateInterval']
            self.__onNotes = set()
            if self.__maxNumSignals is not None: 
                self.__activeNotes = []
                self.__activeTimes = []
                self.__now = time.time()
            print "SETUP output: "+deviceStruct['name']+" connected" 
            
    def __getDeviceId(self,name):
        n_device = pm.get_count()
        foundId = -1
        for id in range(n_device):
            if int(pm.get_device_info(id)[1]==name) & \
                    int(pm.get_device_info(id)[3]==1):
                foundId = id 
        return foundId
        
    def note_on(self,note,velocity):
        '''
        turn the midi-note on
        If maxNumSignals has been set, the note is only turned on if less than
        maxNumSignals are on. Additionally, notes that started more than updateInterval 
        ago are removed from the activeNotes list.
        
        '''  
        self.__onNotes.add(note)
        if self.__maxNumSignals is None:
            super(OutputDevice,self).note_on(note,self.__velocity)
        else:
            now = time.time()
            # update active times of active notes and remove notes from list
            if len(self.__activeTimes)>0:
                done = False
                idx = 0
                while not done:
                    if idx<len(self.__activeTimes):
                        self.__activeTimes[idx]+=now-self.__now
                        if self.__activeTimes[idx]>self.__updateInterval:
                            self.__activeTimes.pop(idx)
                            self.__activeNotes.pop(idx)
                        else:
                            idx+=1
                    else:
                        done=True
            self.__now = now
            if len(self.__activeTimes)<self.__maxNumSignals:
#                print self.__name, note
                super(OutputDevice,self).note_on(note,self.__velocity)
#                if self.__name == OutputHandler.OBJECT:
                print 'note sent', self.__name, self.__now
                if self.__activeNotes.__contains__(note):
                    idx = self.__activeNotes.index(note)
                    self.__activeNotes.remove(note)
                    self.__activeTimes.pop(idx)
                self.__activeNotes.append(note)
                self.__activeTimes.append(0)
            
    def turnAllOff(self):
        for note in self.__onNotes:
            self.note_off(note,100)
        self.__onNotes = set()

class OutputHandler(object):
    NEURON_NOTES = 'SimpleSynth'
    OBJECT = 'MIDISPORT 2x2 Anniv Port A'
    PIANO = 'MIDISPORT 2x2 Anniv Port B'
    VISUALS = 'Ploytec MIDI Cable'
    def __init__(self,outputList=[],neuron2NoteConversion=4):
        super(OutputHandler,self).__init__()
        self.__display = Display(pars['N_col'],pars['N_row'],\
                ['Ne','Ni','s_e','s_i','tau_e','tau_i','midi_ext_e','midi_ext_i',
                 'cam_ext','cam_external_max'],
                'lines')
        self.__name2DeviceStruct = {
                self.NEURON_NOTES:DeviceStruct(),
#                'BCF2000':'Virtual BCF2000',
                self.OBJECT:DeviceStruct(name=self.OBJECT,
                                      maxNumSignals=3,
                                      updateInterval=45,
                                      velocity=30),
                self.PIANO:DeviceStruct(name=self.PIANO,
                                      maxNumSignals=10,
                                      updateInterval=15),
                self.VISUALS:DeviceStruct(name=self.VISUALS,
                                          maxNumSignals=5,
                                          updateInterval=30)
                }
        pm.init()
         #,self.OBJECT,self.PIANO
        self.__setupOutputs(outputList)
        if self.VISUALS in self.__output:
            self.__output[self.VISUALS].note_on(1,100)
#        self.__membraneViewer = Test()
        
        self.__now = time.time()
        self.__activeNotes = set()
        self.__neuron2NoteConversion=neuron2NoteConversion
        
        #Start with one note
#        self.__output['MIDI B'].note_on(1,100)
    
    def __getDevice(self,deviceStruct,instrument=1,maxNumSignals=None):
#        n_device = pm.get_count()
#        foundId = -1
#        for id in range(n_device):
#            if int(pm.get_device_info(id)[1]==deviceStruct['name']) & \
#                    int(pm.get_device_info(id)[3]==1):
#                foundId = id 
#                print 'SETUP: output', deviceStruct['name'], 'connected'
#        print 'SETUP: output', deviceStruct['name'], 'connected'
        return OutputDevice(deviceStruct)
                
#        print "SETUP Warning: output: "+deviceStruct['name']+ " not available!!!"

    def __setupInputs(self,inputList):
        self.__input = {}
        for name in inputList:
            self.__input[name] = self.__getDevice(self.__name2Identifier[name],type='input')
            
    def __setupOutputs(self,outputList):
        self.__output = {}
        for name in outputList:
            self.__output[name] = self.__getDevice(self.__name2DeviceStruct[name])
            
    def updateObjekt(self,fired):
        neuron_ids = intersect1d(fired,pars['note_ids'])
        for neuron_id in neuron_ids:
            self.__output[self.OBJECT].note_on(neuron_id,pars['velocity'])
        
        
    
    def update(self,fired):
#        global pars
#        print 'es feuern', fired
        '''
        if len(self.__midi_timeactive>0):
            self.__midi_timeactive-=time.time()-now
            self.__midi_timeactive = midi_timeactive[midi_timeactive>=0]
        now = time.time()
        '''
        neuron_ids = intersect1d(fired,pars['note_ids'])
        ##################################################
                
        # turn new notes and concious states on and update the allfired-list
        N_fired = neuron_ids.__len__()
        if neuron_ids.__contains__(1):
            self.__neuron2NoteConversion=(4 if self.__neuron2NoteConversion==5 else 5)
            print '----------------------------------------key change'
        if N_fired>0:
            #print neuron_ids
            for neuron_id in neuron_ids:
                for name,output in self.__output.iteritems():
                    if name != self.OBJECT:
                        output.note_on(
                            neuron2note(neuron_id,self.__neuron2NoteConversion),pars['velocity'])
                #if neuron_id>(pars['N']-80):
                #    midi.ausgang_concious.note_on(neuron2note(neuron_id,neuron2note_conversion),pars['velocity'])
                
#                if neuron_id<20:
#                     if midi_timeactive is None:
#                        midi.ausgang_soundextern.note_on(neuron2note(neuron_id,neuron2note_conversion),pars['velocity'])
#                        midi_timeactive = array([1])
#                    elif len(midi_timeactive)<=pars['midi_per_sec']:
#                        midi.ausgang_soundextern.note_on(neuron2note(neuron_id,neuron2note_conversion),pars['velocity'])
#                        midi_timeactive = array(midi_timeactive.tolist().append(1))
#            #if N_fired>=pars['N_concious']:
                #midi_id = mod(N_fired,127)
                #midi_id_extern = mod(N_fired,50)+70
                #print midi_id, N_fired
                
#        self.__membraneViewer.move()        
        # display spikes and update display
        self.__display.update_fired(fired)
        self.__display.update_pars(['cam_ext','midi_ext_e','midi_ext_i','s_e','s_i','tau_e','tau_i','cam_external_max'])
        pygame.display.update()
        
        
    def turnOff(self):
        for outputName in self.__output.iterkeys():
            if outputName  == OutputHandler.NEURON_NOTES:
                self.__output[outputName].turnAllOff()
        '''
                # turn old notes off    
        neuron_ids = intersect1d(fired,pars['note_ids'])
        for neuron_id in neuron_ids:
            midi.ausgang.note_off(neuron2note(neuron_id,neuron2note_conversion),100)
            #midi.ausgang_concious.note_off(neuron2note(neuron_id,neuron2note_conversion),100)
#            midi.ausgang_soundextern.note_off(neuron2note(neuron_id,neuron2note_conversion),100)
            #if neuron_id>(pars['N']-80):
            #    midi.ausgang_concious.note_off(neuron2note(neuron_id,neuron2note_conversion),100)
            #if neuron_id<20:
            #    midi.ausgang_soundextern.note_off(neuron2note(neuron_id,neuron2note_conversion),100)
        #if N_fired>=pars['N_concious']:
        #    midi.ausgang_concious.note_off(midi_id,100)
        #    midi.ausgang_soundextern.note_off(midi_id_extern,100)
        for note_id in range(len(fired)):
            midi.ausgang.note_off(neuron2note(fired[note_id],neuron2note_conversion),100)
        '''




class Display:
    def __init__(self,N_col,N_row,parnames=[],disp_type='dot'):#disp_type='dot',
        pars = parameters()
        # parnames: list of names for the parameters
        self.parnames = parnames
        n_pars = len(parnames)
        self.disp_type = disp_type
        self.N_col = N_col
        self.N_row = N_row
        
        self.spikeScreenSize = (1280,800)#(1920,1050) #(960,525)#
        self.text_color = (100,100,100,0)
        self.textfill_color = (255,255,255,255)
        self.spikefill_color = (0,0,0,0)
        self.spike_color = (255,255,255,255)
        
        self.point_size = 6
        self.point_size = 3 # the point size in case of 'dot'-display
        self.line_width = 3
        self.pointXDist = self.spikeScreenSize[0]/self.N_col # the x-distance between the points
        self.pointYDist = self.spikeScreenSize[1]/self.N_row # the y-distance between the points
        self.border = 5
        self.font_size = 16

        self.text_width = 150
        self.dot_width = N_col*self.pointXDist + 2*self.border
        w =  self.dot_width + self.border + self.text_width
        h = max([(self.N_row+2)*self.pointYDist,(n_pars+1)*self.font_size])
        self.disp_size  = (w,h)
        
        self.screen = pygame.display.set_mode((0,0), 0, 32)
        self.par_surface = pygame.Surface( (self.text_width,h), flags=SRCALPHA, depth=32 )#
        self.par_surface.fill( self.textfill_color )
        pygame.font.init()
        self.font = pygame.font.Font(None, self.font_size)
        text_rect = []
        top=0
        
        self.spikeScreen = pygame.display.set_mode(self.spikeScreenSize, 0, 32)
        self.spikeSurface = pygame.Surface( self.spikeScreenSize, flags=SRCALPHA, depth=32 )#
        self.spikeSurface.fill( self.spikefill_color )
        
#        modes = pygame.display.list_modes(16)
#        pygame.display.set_mode(modes[0], FULLSCREEN, 16)
        
        self.update_pars(parnames)
        
    def update_pars(self,update_names):
        for ii in range(len(update_names)):
            idx = self.parnames.index(update_names[ii])
            text_rect = pygame.Rect((0,idx*self.font_size),(self.text_width,self.disp_size[1]) )
            text = update_names[ii]+": " + small2string(pars[update_names[ii]])
            ren = self.font.render(text,1,self.text_color,self.textfill_color)
            self.par_surface.blit(ren,text_rect)
        self.screen.blit(self.par_surface, (self.dot_width+self.border,0) )
        
    def update_fired(self,fired):
        self.spikeScreen.fill(self.spikefill_color)
        if self.disp_type == 'dot':
            for id in fired:
                coord = linear2grid(id,self.N_col)*(self.pointXDist,self.pointYDist)+self.border
                pygame.draw.circle(self.screen,(0,0,255),coord,self.point_size,0)
        elif self.disp_type == 'lines':
            coord = []
            for id in fired:
                coord.append(linear2grid(id,self.N_col)*(self.pointXDist,self.pointYDist))
            coord = array(coord)+self.border
            #print coord
            if len(coord)>1:
                pygame.draw.lines(self.spikeScreen,self.spike_color,1,coord,self.line_width)
            elif len(coord)==1:
                pygame.draw.circle(self.spikeScreen,self.spike_color,coord[0],self.point_size,0)
        elif self.disp_type == 'square':
            coord = (50,50)#linear2grid(id,self.N_col)*(self.pointXDist,self.pointYDist)+self.border
            ''' TO BE DONE !!! '''
            pygame.draw.rect(self.spikeScreen,self.spike_color,coord,1)
            
            
            
class Membrane_Display:
    def __init__(self,N,vrange=[0,1]):
        import matplotlib.pyplot as pl
        
        plt.rcParams['backend'] = 'macosx'
        pl.rcParams['interactive'] = 'True'
        self.vrange = np.array(vrange)
        #print self.vrange
        self.N = N
        self.nsteps = 100
        #normv = (v-self.vrange[0])/diff(self.vrange)[0]+arange((self.N)-diff(self.vrange)[0]/2)
        #startv = vstack((normv,normv))# resize(normv,[self.nsteps,self.N])
        normv = np.zeros((self.nsteps))
        startv = normv
        for k in range(self.N-1):
            startv = np.vstack((startv,normv+k+1))
        self.fh = pl.figure()   # figure handle
        self.lines = pl.plot(np.transpose(startv))
        pl.ylim(0,self.N)
        pl.xlim(0,self.nsteps)
        pl.draw()
        #pl.show()
    def update(self,v):
        normv = (v-self.vrange[0])/np.diff(self.vrange)+np.arange(self.N)
        for k in range(self.N):
            ndata = [self.lines[k].get_ydata()[idx] for idx in range(1,self.nsteps)]
            ndata.append(normv[k])
            self.lines[k].set_ydata(array(ndata))
        plt.draw()
    def test(self,nrep=100):
        for k in range(nrep):
            v = np.random.rand(self.N)
            self.update(v)
            
            
class MembraneDisplay:
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
#        win = self.fig.canvas.manager.window
#        self.fig.canvas.manager.window.after(100, self.start)
        self.x = np.arange(0, 2*np.pi, 0.01)        # x-array
        self.line, = self.ax.plot(self.x, np.sin(self.x))
        self.line.figure.show()
        self.__i = 0
        
    def start(self):
        for i in np.arange(1,200):
            self.move()
#        self.animate()
        
    def move(self):
        self.__i += 1
        self.line.set_ydata(np.sin(self.x+self.__i/10.0))          # update the data
        self.fig.canvas.draw()                        # redraw the canvas
        print 'moved'
        self.line.figure.show()

class displayTest:
    def __init__(self):
        pygame.init()
        pm.init()
        import time
        self.__display = Display(pars['N_col'],pars['N_row'],\
                ['Ne','Ni','s_e','s_i','tau_e','tau_i','midi_ext_e','midi_ext_i','cam_ext','cam_external_max'],\
                'lines')
    
    def start(self):
        raw_input('feddich wenn Sie es sind...')
        for k in range(1000):
            if k%100==0:
                print 'jetze'
                self.__display.update_fired(array([20,40,70])+2*k)
#                self.__display.update_fired(array([]))
                pygame.display.flip()
                time.sleep(0.1)
    #   

if __name__ == '__main__':
    uwe = Membrane_Display(4)
#    uwe = displayTest()
    uwe.test()

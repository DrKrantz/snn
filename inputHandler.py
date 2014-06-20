
import motmot.cam_iface.choose as cam_iface_choose 
import motmot.cam_iface
from pyglet.gl import *
from pyglet import window
from pyglet import image
from pygarrayimage.arrayimage import ArrayInterfaceImage

from pygame import midi as pm

from numpy import intersect1d, array, asarray,double, mean, abs, diff,unique

from Dunkel_functions import note2neuron
from Dunkel_pars import parameters

#global pars
#pars = parameters()

class Window:
    def __init__(self):
        self.has_exit = False

class WebcamDummy:
    def __init__(self):
        self._dummy = None
        self.window = Window()
    def update(self):
        pass
    def getExternal(self):
        return 0
    
    
class Webcam:
    def __init__(self):
        ############  INITIALIZE WEBCAM   #################
        self.make_cam()
        self.get_image()
        self.aii = ArrayInterfaceImage(self.arr)
        self.arr_old = asarray(self.cam.grab_next_frame_blocking())
        #img = self.aii.texture
        #self.cam_window = make_window(img)
        checks = image.create(32, 32, image.CheckerImagePattern())
        self.background = image.TileableTexture.create_for_image(checks)
        self.make_window()
        self.pars = parameters()
        
    def make_cam(self):
        mode_num = 0
        device_num = 0
        num_buffers = 128
        # next lines taken from motmot documentation
        cam_iface = cam_iface_choose.import_backend('mega', 'ctypes')
        self.cam = cam_iface.Camera(device_num,num_buffers,mode_num)
        self.cam.start_camera()
        
    def update(self):
        arr_old = self.arr
        self.get_image()
        # for some reason, cam.grab_next_frame_blocking() return an array where every second row is dark...
        #arr = arr[:,1:-1:2]
        self.view_image()
        
    def getExternal(self):
        return self.__image2External(double(self.arr),double(self.arr_old))
        
    
    def get_image(self):
        self.arr = asarray(self.cam.grab_next_frame_blocking())
                
    def make_window(self):
        img = self.aii.texture
        self.window = window.Window(visible=False, resizable=True)
        self.window.width = img.width
        self.window.height = img.height
        self.window.set_visible()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
    def view_image(self):
        self.window.flip()
        self.window.dispatch_events()
        # position the background and image in the window
        self.background.blit_tiled(0, 0, 0, self.window.width, self.window.height)
        self.aii.texture.blit(0, 0, 0)
        # switch ArrayInterfaceImage to view the new array
        self.aii.view_new_array(self.arr) 
        
    def __image2External(self,arr,arr_old):
        abs_diff = abs(arr-arr_old)
        mean_diff = mean(abs_diff)
    #    print mean_diff 
    #    [diff_min,diff_max]=[abs_diff.min(),abs_diff.max()]
        if mean_diff<self.pars['diff_min']:
            self.pars['diff_min']=mean_diff
        elif mean_diff>self.pars['diff_max']:
            self.pars['diff_max']=mean_diff
        av_diff =  self.pars['cam_external_range'][0]+\
                diff(self.pars['cam_external_range'])*(mean_diff-self.pars['diff_min'])/\
                self.pars['diff_max']
        av_diff = av_diff*(av_diff>self.pars['cam_thres'])#*ones((pars['Ne']+pars['Ni']))
        return 0#av_diff
    
class InputDevice(pm.Input):
    def __init__(self,name):
        id = self.__getDeviceId(name)
        if id == -1:
            print "SETUP WARNING!!! input: "+name+" not available!!!"
            return None
        else:
            super(InputDevice,self).__init__(id)
            print "SETUP input: "+name+" connected with id", id
        
    def __getDeviceId(self,name):
        n_device = pm.get_count()
        foundId = -1
        for id in range(n_device):
            if int(pm.get_device_info(id)[1]==name) & \
                    int(pm.get_device_info(id)[2]==1):
                foundId = id 
        return foundId
    
    def map_keys(self):
        while True:
            try:
                if self.poll():
                    print self.read(10)
            except KeyboardInterrupt:
                return

class InputHandler(object):
    PARAMETERS = 'Virtual BCF2000'
    OBJECT = 'USB MIDI Device'
    WEBCAM = 'webcam'
    def __init__(self,inputList=[],pars={}):
        self.pars=pars
        self.webcam = Webcam()
        self.__setupInputs(inputList)
        self.__fired = []
    
    @property    
    def webcamOpen(self):
        return self.webcam.window.has_exit
    
    def __setupInputs(self,inputList):
        pm.init()
        self.__inputs = {}
        for name in inputList:
            self.__inputs[name] = InputDevice(name)
    
    def getFired(self):
        fired = array(self.__fired,int)
        self.__fired = []
        return fired
    
    def update(self):
        self.webcam.update()
        ########## CONVERT MIDI INPUT TO NETWORK INPUT AND PROPERTIES ###############
        self.__updateBCF()
#        self.__updateObject()

    def __updateObject(self):
        device = self.__inputs[self.OBJECT]
#        print 'wird gemacht:', device 
        if device.poll():
            self.__fired = []
            data = device.read(self.pars['n_read'])
            data.reverse()
            MIDI_data = array([dd[0] for dd in data])
            [self.__fired.append(dd[1]) for dd in MIDI_data]
            print 'object:', MIDI_data, self.__fired
            
     
    def __updateBCF(self):
        device = self.__inputs[self.PARAMETERS]
        if device.poll():
            data = device.read(self.pars['n_read'])
#            print data
            data.reverse()
            MIDI_data = array([dd[0] for dd in data])
            # extract data from keys
            key_data = MIDI_data[MIDI_data[:,0]==self.pars['midistat_keys'],:]
            if key_data.__len__()>0 and self.pars['midistat_keys']!=None:
                key_data_on = key_data[key_data[:,2]>0,:] # take only "note on"
                if key_data_on.__len__()>0:
                    # this maps the key inputs to external inputs to specific notes (1-to-1)
                    '''  TO BE RE-IMPLEMENTED
                    key_ids_ext = intersect1d(unique(key_data_on[:,1]), self.pars['key_ids_ext'])
                    v[note2neuron(key_ids_ext)]=self.pars['threshold']
                    '''
                    # this maps key inputs to changes in parameters and external inputs, i.e. gradual up/down changes
                    key_ids_pars = intersect1d(unique(key_data_on[:,1]), 
                                               self.pars['key_ids_pars'])
                    self.MIDI2pars(key_data,key_ids_pars,'keys')
                    
            # extract data from sliders
            slide_data = MIDI_data[MIDI_data[:,0]==self.pars['midistat_slide'],:]
            slide_ids_ext = intersect1d(unique(slide_data[:,1]), self.pars['slide_ids_ext'])
            if slide_ids_ext.__len__()>0:
                self.__MIDI2external(slide_data,slide_ids_ext,'slide')
            slide_ids_pars = intersect1d(unique(slide_data[:,1]), self.pars['slide_ids_pars'])
            if slide_ids_pars.__len__()>0:
                self.__MIDI2pars(slide_data,slide_ids_pars,'slide')
  
                    
    def __MIDI2external(self,MIDI_data,in_ids,in_type):
         # convert the MIDI-input to the external input to the neurons
        ids = list(unique(MIDI_data[:,1]))
        if in_type=='slide':
            for id in in_ids:
                action = self.pars['slide_action_ext'][self.pars['slide_ids_ext'].index(id)]
                value = self.pars['ext_step']*MIDI_data[ids.index(id),2]/127
                #print action, value
                if action == 0:
                    #print value
                    self.pars['midi_ext_e'] = value
                    self.pars['midi_ext_i'] = value
                    self.pars['midi_external'][:] = value
                elif action == 1:
                    #print value
                    self.pars['midi_ext_e'] = value
                    self.pars['midi_external'][self.pars['Exc_ids']] = self.pars['midi_ext_e']
                elif action == 2:
                    #print value
                    self.pars['midi_ext_i'] = value
                    self.pars['midi_external'][self.pars['Inh_ids']] = self.pars['midi_ext_i']
                elif action == 3:
                    #print value
                    self.pars['midi_external'][[0,4,9,14,19]] = value
                elif action == 4:
                    #print value
                    midi_external[[24, 29, 34, 39]] = value
        elif in_type=='keys':
            for id in in_ids:
                parid = self.pars['key_action_ext'][self.pars['key_ids_pars'].index(id)]
                if parid==0:
                    self.pars['midi_external']=self.pars['midi_external']-self.pars['ext_step']
                if parid==1:
                    self.pars['midi_external']=self.pars['midi_external']+self.pars['ext_step']
                if parid==2:
                    self.pars['midi_external'][self.pars['Exc_ids']] = self.pars['midi_external'][self.pars['Exc_ids']]-self.pars['ext_step']
                if parid==3:
                    self.pars['midi_external'][self.pars['Exc_ids']] = self.pars['midi_external'][self.pars['Exc_ids']]+self.pars['ext_step']
                if parid==4:
                    self.pars['midi_external'][self.pars['Inh_ids']] = self.pars['midi_external'][self.pars['Inh_ids']]-self.pars['ext_step']
                if parid==5:
                    self.pars['midi_external'][self.pars['Inh_ids']] = self.pars['midi_external'][self.pars['Inh_ids']]+self.pars['ext_step']               
                    
    def __MIDI2pars(self,MIDI_data,in_ids,in_type):
        # convert the MIDI-input into parameter values
        ids = list(unique(MIDI_data[:,1]))
        if in_type=='slide':
            for id in in_ids:
                param = self.pars['slide_action_pars'][self.pars['slide_ids_pars'].index(id)]
                
#                print '-------', param+'_step'
                self.pars[param] = self.pars[param+'_def']+self.pars[param+'_step']*MIDI_data[ids.index(id),2]
        elif in_type=='keys':
            for id in in_ids:
                parid = self.pars['key_action_pars'][self.pars['key_ids_pars'].index(id)]
                if parid==0:
                    self.pars['s_e']=self.pars['s_e']-self.pars['s_e_step']*(self.pars['s_e']>self.pars['s_e_range'][0])
                if parid==1:
                    self.pars['s_e']=self.pars['s_e']+self.pars['s_e_step']*(self.pars['s_e']<self.pars['s_e_range'][1])    
                if parid==2:
                    self.pars['s_i']=self.pars['s_i']-self.pars['s_i_step']*(self.pars['s_i']>self.pars['s_i_range'][0])
                if parid==3:
                    self.pars['s_i']=self.pars['s_i']+self.pars['s_i_step']*(self.pars['s_i']<self.pars['s_i_range'][1])    
                if parid==4:
                    self.pars['tau_e']=self.pars['tau_e']-self.pars['tau_e_step']*(self.pars['tau_e']>self.pars['tau_e_range'][0])
                if parid==5:
                    self.pars['tau_e']=self.pars['tau_e']+self.pars['tau_e_step']*(self.pars['tau_e']<self.pars['tau_e_range'][1])
                if parid==6:
                    self.pars['tau_i']=self.pars['tau_i']-self.pars['tau_i_step']*(self.pars['tau_i']>self.pars['tau_i_range'][0])
                if parid==7:
                    self.pars['tau_i']=self.pars['tau_i']+self.pars['tau_i_step']*(self.pars['tau_i']<self.pars['tau_i_range'][1])
                    
                    
if __name__=='__main__':
    uwe = Webcam()
    import time
    for k in range(20):
        time.sleep(1)
        uwe.update()
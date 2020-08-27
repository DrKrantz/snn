#!/usr/bin/env python

""" webcam.py: the webcam - handler """

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140620

from numpy import asarray, mean, abs, diff, double


import motmot.cam_iface.choose as cam_iface_choose
# import motmot.cam_iface
import pyglet.gl
from pyglet import window
from pyglet import image
from pygarrayimage.arrayimage import ArrayInterfaceImage

from V1.Dunkel_pars import parameters


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
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

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
        av_diff = av_diff*(av_diff>self.pars['cam_thres'])  # *ones((pars['Ne']+pars['Ni']))
        return 0  # av_diff

if __name__=='__main__':
    uwe = Webcam()
    import time
    for k in range(20):
        time.sleep(1)
        uwe.update()
from tkinter import *
from Dunkel_pars import parameters
from pythonosc.udp_client import SimpleUDPClient
import sensoryNetwork

PARAMETERS = ['s_e', 's_i', 'tau_e', 'tau_i', 'lambda_e', 'lambda_i']


class SpikeButton(Frame):
    width = 7

    def __init__(self, parent, title, send_cb, *args):
        super(SpikeButton, self).__init__(parent, *args)
        Label(self, text=title, width=self.width).pack(side=TOP)
        self.button = Button(self, command=lambda: send_cb(title)).pack(side=TOP)


class LabelledSlider(Frame):
    width = 7

    def __init__(self, parent, title, default, par_range, resolution, send_cb, *args):
        super(LabelledSlider, self).__init__(parent, *args)
        self.__send_cb = send_cb
        self.title = title
        self.var = DoubleVar()
        self.var.set(default)

        Label(self, text=title, width=self.width).pack(side=TOP)
        self.slider = Scale(self, from_=par_range[1], to=par_range[0], variable=self.var,
                            command=self.__release_cb, showvalue=0, resolution=resolution, length=150)
        self.slider.pack(side=TOP)
        self.value_label = Label(self, text=self.var.get(), width=self.width)
        self.value_label.pack(side=TOP)

    def __release_cb(self, value):
        self.value_label.config(text=value)
        self.__send_cb(self.title, value)


class Gui(Tk):
    __size = '530x380'
    __title = "Parameter controller"

    def __init__(self, pars, **kwargs):
        super(Gui, self).__init__(**kwargs)
        self.__pars = pars

        self.title(self.__title)
        self.geometry(self.__size)
        self.__create_osc_client()
        self.__create_slider()
        self.__create_buttons()

    def __create_osc_client(self):
        self.__client = SimpleUDPClient(sensoryNetwork.IP, sensoryNetwork.GUI_PORT)

    def __create_slider(self):
        self.slider = {}
        for col, name in enumerate(PARAMETERS):
            slider = LabelledSlider(self, name, self.__pars[name], self.__pars[name + "_range"],
                                    self.__pars[name + "_step"], self.__slider_cb)
            slider.pack(side=LEFT)
            self.slider[name] = slider

    def __create_buttons(self):
        for k in range(5):
            button = SpikeButton(self, k+1, self.__button_cb)
            button.pack(side=TOP)
            self.__buttons = [button]

    def __slider_cb(self, *args):
        self.__client.send_message(sensoryNetwork.GUI_PAR_ADDRESS, args)

    def __button_cb(self, *args):
        self.__client.send_message(sensoryNetwork.GUI_SPIKE_ADDRESS, args)


if __name__ == "__main__":
    gui = Gui(parameters())
    gui.mainloop()

from tkinter import *
import numpy as np
import pickle

import config.osc
from Dunkel_pars import parameters
from pythonosc.udp_client import SimpleUDPClient

PARAMETERS = ['s_e', 's_i', 'tau_e', 'tau_i', 'lambda_e', 'lambda_i']


class OutputController(Frame):
    color = "#312B2F"

    def __init__(self, parent, output_name, *args):
        super(OutputController, self).__init__(parent, bg=self.color)

        self.title = Label(self, text=output_name, width=18, font="Helvetica 16", anchor="w", bg=self.color)
        self.title.pack()

        self.max_num_signals = 0
        self.max_num_signals_slider = Scale(self, label="MaxNumSignals", from_=0, to=10, resolution=1,
                                            command=self.__set_max_num_signals,length=150, orient=HORIZONTAL,
                                            bg=self.color)
        self.max_num_signals_slider.pack(side=TOP)

        self.update_interval = 0
        self.update_interval_slider = Scale(self, label="Update Interval", from_=0, to=60, resolution=5,
                                            command=self.__set_update_interval, length=150, orient=HORIZONTAL,
                                            bg=self.color)
        self.update_interval_slider.pack(side=TOP)

        self.synchrony_limit = 0
        self.synchrony_limit_slider = Scale(self, label="Synchrony Limit", from_=0, to=10, resolution=1,
                                            command=self.__set_synchrony_limit, length=150, orient=HORIZONTAL,
                                            bg=self.color)
        self.synchrony_limit_slider.pack(side=TOP)

    def __set_max_num_signals(self, value):
        self.max_num_signals = value

    def __set_update_interval(self, value):
        self.update_interval = value

    def __set_synchrony_limit(self, value):
        self.synchrony_limit = value


class SpikeButton(Frame):
    width = 7

    def __init__(self, parent, title, send_cb, *args):
        super(SpikeButton, self).__init__(parent, *args)
        # Label(self, text=title, width=self.width).pack(side=RIGHT)
        self.button = Button(self, command=lambda: send_cb(title))
        self.button.pack(side=LEFT)


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
        self.var.set(value)
        self.value_label.config(text=value)
        self.__send_cb(self.title, value)

    def get(self):
        return self.var.get()


class Gui(Tk):
    __size = '930x380'
    __title = "Parameter controller"

    def __init__(self, pars, **kwargs):
        super(Gui, self).__init__(**kwargs)
        Label(self, text="Balance", width=7).pack(side=TOP)
        self.__balance_label = Label(self, text=0, width=7)
        self.__balance_label.pack(side=TOP)
        self.__reset_button = Button(self, command=self.__reset_cb, text="RESET")
        self.__reset_button.pack(side=TOP)

        self.__pars = pars

        self.title(self.__title)
        self.geometry(self.__size)
        self.__create_osc_client()
        self.__create_slider()
        # self.__create_buttons()
        self.__create_output_controller()
        self.__reset_cb()

    def __create_osc_client(self):
        self.__client = SimpleUDPClient(config.osc.IP, config.osc.GUI_PORT)

    def __create_slider(self):
        self.slider = {}
        for col, name in enumerate(PARAMETERS):
            slider = LabelledSlider(self, name, self.__pars[name], self.__pars[name + "_range"],
                                    self.__pars[name + "_step"], self.__slider_cb)
            slider.pack(side=LEFT)
            self.slider[name] = slider

    def __create_buttons(self):
        for k in range(10):
            button = SpikeButton(self, k+70, self.__button_cb)
            button.pack(side=TOP)
            self.__buttons = [button]

    def __create_output_controller(self):
        self.__output_controller = OutputController(self, "piano".upper())
        self.__output_controller.pack(side=LEFT)

    def __slider_cb(self, *args):
        self.__client.send_message(config.osc.GUI_PAR_ADDRESS, args)

    def __button_cb(self, *args):
        self.__client.send_message(config.osc.GUI_SPIKE_ADDRESS, args)

    def __reset_cb(self):
        self.__client.send_message(config.osc.GUI_RESET_ADDRESS, pickle.dumps(self.__pars))
        for name, slider in self.slider.items():
            slider.var.set(self.__pars[name])
            slider.value_label.config(text=self.__pars[name])

    def __update_balance(self):
        balance = self.slider['s_e'].get() * self.slider['lambda_e'].get() - \
                  self.slider['s_i'].get() * self.slider['lambda_i'].get()
        self.__balance_label.config(text=np.around(balance, decimals=10))
        self.after(500, self.__update_balance)

    def start(self):
        self.after(500, self.__update_balance)
        self.mainloop()


if __name__ == "__main__":
    gui = Gui(parameters())
    gui.start()

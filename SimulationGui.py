from tkinter import *
import pickle

import config.osc
from Dunkel_pars import parameters
from pythonosc.udp_client import SimpleUDPClient

PARAMETERS = ['s_e', 's_i', 'tau_e', 'tau_i', 'lambda_e', 'lambda_i']


class OutputController(Frame):
    color = "#312B2F"

    def __init__(self, parent, output_name, *args):
        super(OutputController, self).__init__(parent, bg=self.color, bd=2, relief="groove")

        self.title = Label(self, text=output_name, width=8, font="Helvetica 16", anchor="w", bg=self.color)
        self.send_button = Button(self, command=self.__send, text="send")
        self.reset_button = Button(self, command=self.__reset, text="reset")
        self.max_num_signals = HorizontalSlider(self, "MaxNumSignals", 0, 10, 1, bg=self.color)
        self.update_interval = HorizontalSlider(self, "Update Interval", 0, 60, 5, bg=self.color)
        self.synchrony_limit = HorizontalSlider(self, "Synchrony Limit", 0, 10, 1, bg=self.color)

        self.title.grid(column=0, row=0)
        self.reset_button.grid(column=1, row=0)
        self.send_button.grid(column=2, row=0)
        self.max_num_signals.grid(column=0, row=1, columnspan=3)
        self.update_interval.grid(column=0, row=2, columnspan=3)
        self.synchrony_limit.grid(column=0, row=3, columnspan=3)

    def __send(self):
        self.max_num_signals.set_current()
        self.update_interval.set_current()
        self.synchrony_limit.set_current()

    def __reset(self):
        pass


class SpikeButton(Frame):

    def __init__(self, parent, title, send_cb, *args):
        super(SpikeButton, self).__init__(parent, *args)
        self.button = Button(self, text=title, width=1, command=lambda: send_cb(title))
        self.button.pack(side=LEFT)


class HorizontalSlider(Frame):
    def __init__(self, parent, title, from_, to, resolution, **kwargs):
        super(HorizontalSlider, self).__init__(parent, **kwargs)

        self.var = IntVar(value=0)
        self.slider = Scale(self, label=title, from_=from_, to=to, resolution=resolution,
                            command=self.__slider_release_cb, length=180, orient=HORIZONTAL,
                            **kwargs)
        self.current_label = Label(self, width=2, text=self.var.get(), **kwargs)

        self.slider.grid(column=0, row=0)
        self.current_label.grid(column=1, row=0)

    def __slider_release_cb(self, value):
        self.var.set(value)
        self.current_label.config(fg='blue')

    def set_current(self):
        self.current_label.config(text=self.var.get(), fg='white')


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
    __size = '510x510'
    __title = "Parameter controller"
    pady=10

    def __init__(self, pars, **kwargs):
        super(Gui, self).__init__(**kwargs)
        self.__pars = pars

        self.title(self.__title)
        self.geometry(self.__size)
        self.__client = SimpleUDPClient(config.osc.IP, config.osc.GUI_PORT)

        self.slider_frame = self.__create_slider()
        self.spike_button_frame = self.__create_buttons()
        self.piano_frame = OutputController(self, "piano".upper())
        self.visuals_frame = OutputController(self, "visuals".upper())

        # self.reset_button.grid(column=1, row=0)
        self.slider_frame.grid(column=0, row=1, columnspan=2, pady=self.pady)
        self.spike_button_frame.grid(column=0, row=2, columnspan=2, pady=self.pady)
        self.piano_frame.grid(column=0, row=3, pady=self.pady)
        self.visuals_frame.grid(column=1, row=3, pady=self.pady)

        self.__reset_cb()

    def __create_slider(self):
        self.slider = {}
        slider_frame = Frame(self,  bd=2, relief="groove")
        for col, name in enumerate(PARAMETERS):
            slider = LabelledSlider(slider_frame, name, self.__pars[name], self.__pars[name + "_range"],
                                    self.__pars[name + "_step"], self.__slider_cb)
            slider.pack(side=LEFT)
            self.slider[name] = slider

        reset_button = Button(slider_frame, command=self.__reset_cb, text="RESET")
        reset_button.pack(side=BOTTOM)
        return slider_frame

    def __create_buttons(self):
        spike_button_frame = Frame(self,  bd=2)
        for k in range(10):
            button = SpikeButton(spike_button_frame, k+70, self.__button_cb)
            button.pack(side=LEFT)
            self.__buttons = [button]
        return spike_button_frame

    def __slider_cb(self, *args):
        self.__client.send_message(config.osc.GUI_PAR_ADDRESS, args)

    def __button_cb(self, *args):
        self.__client.send_message(config.osc.GUI_SPIKE_ADDRESS, args)

    def __reset_cb(self):
        self.__client.send_message(config.osc.GUI_RESET_ADDRESS, pickle.dumps(self.__pars))
        for name, slider in self.slider.items():
            slider.var.set(self.__pars[name])
            slider.value_label.config(text=self.__pars[name])

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    gui = Gui(parameters())
    gui.start()

from tkinter import *
from Dunkel_pars import parameters

PARAMETERS = ['s_e', 's_i', 'tau_e', 'tau_i']


class LabelledSlider(Frame):
    width = 7

    def __init__(self, parent, title, par_range, resolution, *args):
        super(LabelledSlider, self).__init__(parent, *args)

        Label(self, text=title, width=self.width).pack(side=TOP)
        self.slider = Scale(self, from_=par_range[1], to=par_range[0],
                            command=self.__print_selection, showvalue=0, resolution=resolution, length=150)
        self.slider.pack(side=TOP)
        self.value_label = Label(self, text=par_range[1], width=self.width)
        self.value_label.pack(side=TOP)

    def __print_selection(self, value):
        self.value_label.config(text=value)

    @property
    def value(self):
        return self.slider.get()


class Gui(Tk):
    __size = '530x380'
    __title = "Parameter controller"

    def __init__(self, parameters, **kwargs):
        super(Gui, self).__init__(**kwargs)
        self.__pars = parameters

        self.title("Parameter controller")

        self.title(self.__title)
        self.geometry(self.__size)
        self.__create_slider()

    def __create_slider(self):
        self.slider = {}
        for col, name in enumerate(PARAMETERS):
            slider = LabelledSlider(self, name, self.__pars[name + "_range"], self.__pars[name + "_step"])
            slider.pack(side=LEFT)
            self.slider[name] = slider


if __name__ == "__main__":
    pars = parameters()
    gui = Gui(pars)
    gui.mainloop()

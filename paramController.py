from tkinter import *


class LabelledSlider(Frame):
    def __init__(self, parent, title, min_val, max_val,  *args):
        super(LabelledSlider, self).__init__(parent, *args)

        Label(text=title).grid()
        self.value_label = Label(text=min_val)
        self.value_label.grid()
        self.slider = Scale(self, from_=max_val, to=min_val,
                            command=self.__print_selection, showvalue=0, resolution=0.01)
        self.slider.grid()

    def __print_selection(self, value):
        self.value_label.config(text=value)


class Gui(Tk):
    __size = '530x380'
    __title = "Parameter controller"

    def __init__(self, **kwargs):
        super(Gui, self).__init__(**kwargs)

        self.title("Parameter controller")

        self.title(self.__title)
        self.geometry(self.__size)
        self.__create_slider()

    def __create_slider(self):
        slider = LabelledSlider(self, 'Wert', 0.0, 1.0)
        slider.grid()


if __name__ == "__main__":
    gui = Gui()
    gui.mainloop()

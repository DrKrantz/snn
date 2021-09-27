#!/usr/bin/env python

""" DOCSTRING """

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140930

import os
import tkinter as tk
import tkFileDialog

class FileSelector(tk.Frame):
    def __init__(self, setFilenameCb, master=None, path='.', ):
        tk.Frame.__init__(self, master)
        self.__setFilename = setFilenameCb
        self.__createWidgets(path)
        self.__layout()

    def __layout(self):
        self.master.title("Select Settings File")
        self.__chooseBtn.grid(column=0,row=0)
        self.__folderInfo.grid(column=1,row=0)
        # self.__startBtn.grid(column=0,row=1)

        self.pack()

    def __createWidgets(self, path):
        # self.__startBtn = tk.Button(self)
        # self.__startBtn['text'] = 'Done'
        # self.__startBtn['fg'] = 'red'
        # self.__startBtn['command'] = self.__loopover

        self.__folderTxt = tk.Label(self)
        self.__folderTxt["text"] = 'Ordner: '
        self.__folderInfo = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.__folderInfo["text"] = 'Please choose settings-file'

        self.__chooseBtn = tk.Button(self)
        self.__chooseBtn["text"] = 'File'
        self.__chooseBtn['command'] = self.__chooseCb



#        self.__convertingLabel = tk.Label(self)
#        self.__convertingLabel["text"] = 'schrumpfe:'
#         self.__status = StatusBar(self)
#         self.__status.set('ich warte...')

    def __chooseCb(self):
        filename = tkFileDialog.askopenfilename(title='Choose settings-file')
        if filename:
            self.__folderInfo['text'] = filename
            self.__folderInfo.update_idletasks()
            self.__setFilename(filename)

#     def __loopover(self):
#         self.__imageDir = self.__folderInfo['text']
#         fileList = os.listdir(self.__imageDir)
#         self.__status.set('ich arbeite ...')
#         for file in fileList:
#             name,ext = os.path.splitext(file)
#
#             if ext.lower() in FORMATS:
#
#                 Converter(file,self.__imageDir)
# #                self.__status.clear()
#             else:
#                 pass
# #            print 'fehler in', file
#         self.__status.set('Fertig!')


    # def quit(self):
    #     print 'uwe'
    #     super(FileSelector,self).quit()

if __name__=='__main__':
#    uwe = Converter('test1.jpeg')
    app = FileSelector()
    # app.mainloop()

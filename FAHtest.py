from playsound3 import playsound
#import time
from os import path
#import psutil
bundle_dir = path.abspath(path.dirname(__file__))
path_to_sound = path.join(bundle_dir, 'FAH.mp3')
path_to_settings = path.join(bundle_dir, 'settings.json')
#for proc in psutil.process_iter():
#    print(proc.name())

from pathlib import Path
def fah():
    playsound(path_to_sound,False)
import json
with open(path_to_settings) as f:
    settings=json.load(f)
print(f'testhome: {Path.home()}')

print(settings)
from tkinter import *
root = Tk()
root.title("")
mainframe = Frame(root)
entervar = StringVar()
entervar.set(settings['test'])
button = Button(mainframe,font=('Comic Sans',40),text="FAH",command=fah)
input = Entry(mainframe, textvariable=entervar)
mainframe.grid(padx=15,pady=15)
button.grid(column=1,row=1)
input.grid(column=1,row=2)
root.mainloop()
settings['test']=entervar.get()
with open(path_to_settings,"w") as f:
    json.dump(settings,f)

#appdata
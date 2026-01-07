from tkinter import *
from os import path, makedirs
from pathlib import Path
import json
from playsound3 import playsound
import websockets
import asyncio

version = "0.3.0"
exe_path = path.abspath(path.dirname(__file__))
config_path = Path.home() / "AppData" / "Local" / "FAHBot"
template_path = path.join(exe_path, 'settings.json')
fah_path = path.join(exe_path, "FAH.mp3")




def main():

    root = Tk()
    root.title("FAHBot")
    mainframe = Frame(root)
    titlevar = StringVar()
    checkvar = IntVar()
    titlevar.set("FAH INTERACTION TEST")
    title = Label(mainframe, textvariable=titlevar, font = ("Comic Sans MS",40))
    #toggle = Button(mainframe, font = ("Impact",25), text = "Connect", command = executeConnection)

    mainframe.grid(padx=50,pady=50)
    title.grid(column=1,row=1)
    #toggle.grid(column=1,row=2)

    
    async def client():
        url = "ws://localhost:2288"
        async with websockets.connect(url) as websocket:
            await websocket.send("HELLO SERVER")
            reply = await websocket.recv()
            print(reply)

    asyncio.run(client())
    #root.mainloop()






def startup():
    '''
    opens a UI for user to initialize application
    :return:
    '''


    root = Tk()
    root.title("Startup")
    mainframe = Frame(root)

    started = IntVar()
    started.set(0)




    def runInit():
        '''
        Initializes the program by creating the proper file paths and .json files to store data
        '''

        if not (config_path/"config.json").exists():                #check if filebase exists
            try:                                                    #not:
                makedirs(config_path)                               #attempt to create folder
            except FileExistsError:
                pass                                                #if folder exists, eh
            except WindowsError as err:
                print(err)                                          #windows throws something, meh
                return
            with open(template_path) as f:                          #dump template with current version in
                settings = json.load(f)
            settings["Version"]=version
            with open(config_path/"config.json","w") as f:
                json.dump(settings,f)
        else:                                                       #file on: if we're here then the file exists
            with open(config_path/"config.json") as f:              #either the version is out of date or something's bad
                old_settings = json.load(f)
            new_settings = json.load(open(template_path))           #update json in case of new format (TEMPORARY)
            for key in new_settings:
                if key in old_settings.keys():
                    new_settings[key]=old_settings[key]
            new_settings["Version"] = version
            with open(config_path/"config.json","w") as f:          #Eventually will be update check
                json.dump(new_settings,f)


        started.set(1)
        root.destroy()


    initButton = Button(mainframe,font=('Impact',30),text="Initialize",command=runInit)

    mainframe.grid(padx=15,pady=15)
    initButton.grid(column=1,row=1)
    root.mainloop()
    if started.get()==1:
        main()


if __name__ == "__main__":
    if (config_path/"config.json").exists():                            #Check if config file established
        with open(config_path/"config.json") as f:
            try:
                temp_config = json.load(f)
            except:
                startup()
        try:
            if temp_config["Version"] == version:       #Check if .exe was updated
                main()
            else:
                startup()
        except:
            startup()
    else:
        startup()



'''
starting screen that just has a button to initialize
to not load everything through the cybercapture
need flag to not reinitialize if its the same exe file
and then need more tests for having the appdata file already
'''


#far future: select file creation path
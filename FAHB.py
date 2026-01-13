from tkinter import *
from os import path, makedirs
from pathlib import Path
import json
from playsound3 import playsound
import websockets
import asyncio
import threading

version = "0.5.0"
exe_path = path.abspath(path.dirname(__file__))
config_path = Path.home() / "AppData" / "Local" / "FAHBot"
template_path = path.join(exe_path, 'settings.json')
fah_path = path.join(exe_path, "FAH.mp3")
global titlevar


TEMP_sid = 1026245797450371142
TEMP_uid = 361861240395661312

def main():


    async_loop = asyncio.new_event_loop()

    messages = asyncio.Queue()
    def ping():
        async def innerping():
            await messages.put('hello button')
        asyncio.run_coroutine_threadsafe(innerping(),async_loop)


    root = Tk()
    root.title("FAHBot")
    mainframe = Frame(root)
    global titlevar
    titlevar = StringVar()
    titlevar.set("FAH INTERACTION TEST")
    title = Label(mainframe, textvariable=titlevar, font = ("Comic Sans MS",40))
    toggle = Button(mainframe, font = ("Impact",25), text = "Connect", command = ping)

    mainframe.grid(padx=50,pady=50)
    title.grid(column=1,row=1)
    toggle.grid(column=1,row=2)

    async def sendit(websocket):
        while True:
            message = await messages.get()
            await websocket.send(message)

    async def client():
        url = "ws://localhost:2288"
        async with websockets.connect(url) as websocket:
            global titlevar
            asyncio.get_running_loop().create_task(sendit(websocket))   #expand to subfunc to enable basically every button? maybe only one send but each button just passes coords for status change
            client_profile = (TEMP_uid,TEMP_sid)
            await websocket.send(json.dumps(client_profile))
            while True:
                print("waiting")
                message = await websocket.recv()
                print(message)
                titlevar.set(message)


    def startClient():
        async_loop.create_task(client())
        async_loop.run_forever()


    threading.Thread(target=startClient, daemon=True).start()

    root.mainloop()






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


'''
update schema:
so basically there's only the one websocket. this sends messages to the server tagged with their id
the server sends back messages tagged as system or sound or connection or whatever
sound messages are processed into their own handler, download local sounds
need an exception for nondownloaded sounds playing
sound download on startup, on name input, whatever
hmm actually there is a form of doxxing
you put in anybody's name and it'll give you the list of songs in their server
so you probably have to manually put in ids to be safe for each server you want it in
this also allows you to manage your own downloaders
cause otherwise there could be malicious actors who megadownload some 100gb of files'''
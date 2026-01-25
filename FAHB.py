from tkinter import *
from os import path, makedirs
from pathlib import Path
import json
from playsound3 import playsound
import websockets
import asyncio
import threading
import pytubefix

version = "0.5.7"
exe_path = path.abspath(path.dirname(__file__))
config_path = Path.home() / "AppData" / "Local" / "FAHBot"
template_path = path.join(exe_path, 'settings.json')
fah_path = path.join(exe_path, "FAH.mp3")
global titlevar
global settingsvar


TEMP_sid = 1026245797450371142
TEMP_uid = 361861240395661312

def main():


    async_loop = asyncio.new_event_loop()

    messages = asyncio.Queue()
    def ping():
        """
        Converts tkinter button input to asyncio process.
        Sends specific message from button through to the sender.

        :return: None
        """
        async def inner_ping():
            await messages.put('hello button')
        asyncio.run_coroutine_threadsafe(inner_ping(),async_loop)


    root = Tk()
    root.title("FAHBot")
    mainframe = Frame(root)
    global titlevar
    titlevar = StringVar()
    global settingsvar
    settingsvar = StringVar()
    titlevar.set("FAH INTERACTION TEST")
    title = Label(mainframe, textvariable=titlevar, font = ("Comic Sans MS",40))
    toggle = Button(mainframe, font = ("Impact",25), text = "Connect", command = ping)
    userid = Entry(mainframe, textvariable=settingsvar)
    mainframe.grid(padx=50,pady=50)
    title.grid(column=1,row=1)
    toggle.grid(column=1,row=2)

    async def send_it(websocket):
        """Persistently sends any outgoing messages in the queue"""
        while True:
            message = await messages.get()
            await websocket.send(message)

    def playit(file):
        print("playing it")
        print((config_path/"MP3"/(file+'.mp3')))
        playsound((config_path/"MP3"/(file+'.mp3')))

    def sound_adder(keyword, link):
        aud = pytubefix.YouTube(link)
        print(aud)
        aud.streams.filter(only_audio=True)
        print(aud.streams.filter(only_audio=True))
        print(aud.streams.get_audio_only())
        aud.streams.get_audio_only().download(filename=keyword+'.mp3',output_path=str((config_path/"MP3")))


    async def client():
        """Is a websocket client"""
        url = "ws://localhost:2288"
        async with websockets.connect(url) as websocket:
            global titlevar
            global settingsvar
            asyncio.get_running_loop().create_task(send_it(websocket))   #expand to subfunc to enable basically every button? maybe only one send but each button just passes coords for status change
            client_profile = (TEMP_uid,TEMP_sid)                                    # ^ also simultaneously it writes to the json. evry button thru one
            await websocket.send(json.dumps(client_profile))
            while True:
                print("waiting")
                message = await websocket.recv()
                message = json.loads(message)
                print(message)
                if message[0] == 'addsound':
                    sound_adder(message[1][0],message[1][1])
                elif message[0] == 'removesound':
                    pass                                                    #add and remove sounds while live, we add a database refernce when client starts to check stored sounds against all sounds.
                elif message[0] == 'playsound':
                    threading.Thread(target=playit, args=(message[1],)).start()
                print(message)

                titlevar.set(message)



    def start_client():
        """Begins the asyncio loop"""
        async_loop.create_task(client())
        async_loop.run_forever()


    threading.Thread(target=start_client, daemon=True).start()

    root.mainloop()






def startup():
    """
    Opens a UI for user to initialize application.
    This helps not do too much while antiviruses are evaluating program,
    due to py.exe's not being trusted.
    """


    root = Tk()
    root.title("Startup")
    mainframe = Frame(root)

    started = IntVar()
    started.set(0)




    def run_init():
        """
        Initializes the program by creating the proper file paths and .json files to store data
        """
        if not ((config_path/"config.json").exists()):                #check if filebase exists
            try:                                                    #not:
                makedirs(config_path)                       #attempt to create folder
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
        if not (config_path/"MP3").exists():
            try:
                makedirs(config_path/"MP3")
            except FileExistsError:
                pass                                         # if folder exists, eh
            except WindowsError as err:
                print(err)                                  # windows throws something, meh
                return

        started.set(1)
        root.destroy()


    init_button = Button(mainframe,font=('Impact',30),text="Initialize",command=run_init)

    mainframe.grid(padx=15,pady=15)
    init_button.grid(column=1,row=1)
    root.mainloop()
    if started.get()==1:
        main()


if __name__ == "__main__":
    if (config_path/"config.json").exists() and (config_path/"MP3").exists():                            #Check if config file established
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
import asyncio
import websockets
import time
import mysql.connector
import discord
import json

mydb = mysql.connector.connect(host='localhost',user='Conch',password='WizardConch1!',database='fahbot')
db = mydb.cursor()


def bot_handler(message, websocket):
    msg_id = message[0]
    if msg_id=='startup':
        print(f"WE GOT A STARTUP MESSAGE: {message}")
    elif msg_id=='addserver':
        pass
    elif msg_id=='removeserver':
        pass
    elif msg_id=='serversettings':
        pass
    elif msg_id=='addsound':
        pass
    elif msg_id=='removesound':
        pass
    elif msg_id=='playsound':
        pass


def client_handler(message, websocket):
    pass





async def server(websocket):
    async for message in websocket:
        message = json.loads(message)
        if message[0]=='b':
            bot_handler(message[1],websocket)
        elif message[0]=='c':
            client_handler(message[1],websocket)


async def main():
    async with websockets.serve(server, "localhost",2288):
        print("Server running")
        await asyncio.Future()

asyncio.run(main())
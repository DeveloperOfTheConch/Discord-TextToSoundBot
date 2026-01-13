import asyncio
import websockets
import time
import mysql.connector
import discord
import json

mydb = mysql.connector.connect(host='localhost',user='Conch',password='WizardConch1!',database='fahbot')
db = mydb.cursor()


clients = {}

async def bot_handler(websocket):
    async for message in websocket:
        message = json.loads(message)
        msg_id = message[0]
        if msg_id=='startup':
            localkeys={}
            print(f"WE GOT A STARTUP MESSAGE: {message}")
            sql = 'SELECT word FROM sound WHERE id=%s'
            for value in message[1]:

                db.execute(sql,[value])
                vals = db.fetchall()
                for v in range(len(vals)):
                    vals[v] = vals[v][0]
                localkeys[value]=vals
            await websocket.send(json.dumps(['startup',localkeys]))

        elif msg_id=='addserver':
            pass
        elif msg_id=='removeserver':
            pass
        elif msg_id=='serversettings':
            pass
        elif msg_id=='addsound':
            sql= "INSERT INTO sound (id, word, link) VALUES (%s, %s, %s)"
            val = (message[1],message[2],message[3])
            db.execute(sql, val)
            mydb.commit()
            print(db.rowcount, "record inserted")
        elif msg_id=='removesound':
            sql = 'DELETE FROM sound WHERE id=%s AND word=%s'
            val = (message[1], message[2])
            db.execute(sql,val)
            mydb.commit()
            print(db.rowcount, "sound deleted")
        elif msg_id=='playsound':
            pass


async def client_handler(websocket):
    clients[websocket]=[]
    print(f'client {websocket} connected!')
    try:
        async for message in websocket:
            print(message)
    except websockets.exceptions.ConnectionClosedError:
        pass
    finally:
        clients.pop(websocket, None)
        print(f'client {websocket} disconnected!')



async def main():
    async with websockets.serve(client_handler, "localhost",2288), websockets.serve(bot_handler, "localhost", 2299):
        print("Server running")
        await asyncio.Future()

asyncio.run(main())
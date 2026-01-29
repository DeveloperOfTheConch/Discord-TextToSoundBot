import asyncio
import websockets
import time
import mysql.connector
import discord
import json
import uuid

mydb = mysql.connector.connect(host='localhost',user='Conch',password='WizardConch1!',database='fahbot')
db = mydb.cursor()
b_uid = 1459047155888291968


connected_clients = {}

async def bot_handler(websocket):
    """
    Handles messages incoming from the Discord bot.
    Switches based on incoming message id.
    """
    async for message in websocket:
        message = json.loads(message)
        msg_id = message[0]
        if msg_id=='startup':
            print(f"WE GOT A STARTUP MESSAGE: {message}")
            db.execute("DELETE FROM discord_profiles")
            mydb.commit()
            localkeys={}

            sql = 'SELECT word FROM sound WHERE id=%s'
            for value in message[1]:

                db.execute(sql,[value[0]])
                vals = db.fetchall()
                for v in range(len(vals)):
                    vals[v] = vals[v][0]
                localkeys[value[0]]=vals
            await websocket.send(json.dumps(['startup',localkeys]))
            sql = "INSERT INTO discord_profiles (sid,uid) VALUES (%s, %s)"


            for values in message[1]:
                for members in values[1]:
                    db.execute(sql,(values[0],members))
            mydb.commit()


        elif msg_id=='addserver':
            sql = "INSERT INTO discord_profiles (sid, uid) VALUES (%s, %s)"
            val = (message[1][0],message[1][1])    #FIX THIS DO THE SAME LOOP AS ABOVE
            db.execute(sql,val)
            mydb.commit()

        elif msg_id=='removeserver':
            sql = "DELETE FROM discord_profiles WHERE sid=%s"       #also have it delete the settings
            val = (message[1],)
            db.execute(sql, val)
            mydb.commit()

        elif msg_id=='addmember':
            sql = 'INSERT INTO discord_profiles (sid, uid) VALUES (%s, %s)'
            val = (message[1][1],message[1][0])
            db.execute(sql, val)
            mydb.commit()

        elif msg_id=='removemember':
            sql = 'DELETE FROM discord_profiles WHERE sid=%s AND uid=%s'
            val = (message[1],[1], message[1][0])
            db.execute(sql, val)
            mydb.commit()

        elif msg_id=='serversettings':
            pass

        elif msg_id=='addsound':
            sql= "INSERT INTO sound (id, word, link) VALUES (%s, %s, %s)"
            val = (message[1][0],message[1][1],message[1][2])
            db.execute(sql, val)
            mydb.commit()
            print(db.rowcount, "record inserted")


            for client in connected_clients.values():
                m = json.dumps(["addsound",[message[1][1],message[1][2]]])
                await client.send(m)


        elif msg_id=='removesound':
            sql = 'DELETE FROM sound WHERE id=%s AND word=%s'
            val = (message[1], message[2])
            db.execute(sql,val)
            mydb.commit()
            print(db.rowcount, "sound deleted")






        elif msg_id=='playsound':


            sql = 'SELECT uuid FROM server_profiles INNER JOIN discord_profiles ON server_profiles.s_uid = discord_profiles.uid AND server_profiles.s_sid = discord_profiles.sid'
            db.execute(sql)
            users = db.fetchall()
            for u in users:
                await connected_clients[u[0]].send(json.dumps(['playsound',message[1]]))




        elif msg_id=='targetsound':
            pass

#send sound to each client who has the server
#when client connects, access the uhh list of sounds per server
#download sound button



#async def dispatcher(websocket):
 #   while True:
  #      message = await client_messages.get()



def client_handler(websocket, message, client_id):

    msg_id = message[0]
    msg = message[1]

    if msg_id == 'c_id':
        sid = msg[0]
        uids = msg[1]

        nsql = 'INSERT INTO server_profiles (uuid, s_uid, s_sid) select %s, %s, %s WHERE NOT EXISTS(SELECT 1 from server_profiles WHERE uuid=%s AND s_uid = %s AND s_sid = %s);'
        for u in uids:
            val = (client_id, int(u), sid, client_id, int(u), sid)
            db.execute(nsql, val)
            mydb.commit()





async def client_connector(websocket):
    """Handles connections of each client application to the server"""
    client_id = str(uuid.uuid4())
    connected_clients[client_id]=websocket
    print(f'client {websocket} connected!')

    try:
        async for message in websocket:
            client_handler(websocket, json.loads(message), client_id)
    except websockets.exceptions.ConnectionClosedError:
        pass
    finally:
        print(asyncio.get_running_loop())
        connected_clients.pop(client_id, None)
        print(f'client {client_id} disconnected!')
        sql = "DELETE FROM server_profiles WHERE uuid=%s"
        val = [client_id]
        db.execute(sql,val)
        mydb.commit()




async def main():
    async with websockets.serve(client_connector, "localhost",2288), websockets.serve(bot_handler, "localhost", 2299):
        print("Server running")
        await asyncio.Future()

asyncio.run(main())



#verified dbs: one from connected appl. where combines uuid w/ provided tags
#and one just with the keypairs of existing accounts in servers
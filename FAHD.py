import discord
import asyncio
import websockets
import threading
import json
import os
import requests
import pytubefix

bot = discord.Bot(intents=discord.Intents.all())

local_keywords = {}

def main():




    @bot.event
    async def on_guild_join(guild):
        send(['addserver',[guild.id,[m.id for m in guild.members]]])

    @bot.event
    async def on_guild_remove(guild):
        send(['removeserver',guild.id])

    @bot.event
    async def on_member_join(member):
        send(['addmember',[member.id,member.guild.id]])

    @bot.event
    async def on_member_remove(member):
        send(['removemember',[member.id,member.guild.id]])

    @bot.event
    async def on_ready():
        ids = [ [123, [456]], [112233, [12, 34]] ]
        for i in bot.guilds:
            ids.append([i.id,[m.id for m in i.members]])
        send(['startup',ids])                           #add while loop so it persistently tries in case server down
        await asyncio.sleep(3)
        print(f'{bot.user} is now online')



    @bot.event
    async def on_message(message):
        print(message.content)
        if message.author == bot.user:
            return
        keywords = local_keywords[message.guild.id]
        if message.content in keywords:
            send(["playsound",message.content])


    @bot.slash_command(description="Add a sound: /addsound <keyword> <link>")
    async def addsound(ctx, keyword, link):
        sid = ctx.guild.id
        if len(keyword)>32:
            await ctx.respond("Keyword cannot be longer than 32 characters!")
            return
        if keyword in local_keywords[sid]:
            await ctx.respond(f'{keyword} is already a keyword!')
            return
        if "https://www.youtube.com/watch?v=" not in link:
            await ctx.respond(f"{link} is not a valid YouTube link.")
            return
        if "Video unavailable" in requests.get(link).text:
            await ctx.respond("YouTube video is not available.")
            return
        vid = pytubefix.YouTube(link)
        if vid.length > 10:
            await ctx.respond('YouTube video is too long! 10 seconds maximum.')
            return
        send(["addsound",[ctx.guild.id,keyword,link]])
        await ctx.respond(f"New sound added with keyword {keyword} successfully.")
        local_keywords[sid].append(keyword)



    @bot.slash_command(description="Remove a sound: /removesound <keyword>")
    async def removesound(ctx, keyword):
        sid = ctx.guild.id
        if keyword not in local_keywords[sid]:
            ctx.respond(f'{keyword} is not an established keyword.')
            return
        send(["removesound", sid, keyword])
        await ctx.respond(f'Sound with keyword {keyword} removed.')
        local_keywords[sid].remove(keyword)

    @bot.slash_command(description="List all keywords (and maybe the links they're mapped to?")
    async def listsounds(ctx):
        soundlist = local_keywords[ctx.guild.id]
        s=""
        for i in soundlist:
            s+= i
            s+='\n'
        if s=="":
            s="No current sounds declared! Use /addsound to get started."
        await ctx.respond(s)

    @bot.slash_command(description='Play a sound targeted at a specific user, dependent on preferences.')
    async def playsound(ctx, member: discord.Member, sound):
        if member not in ctx.guild.members:
            await ctx.respond("User not in server.")
        if sound not in local_keywords[ctx.guild.id]:
            await ctx.respond(f'{sound} is not a valid keyword!')
        send(["targetsound",member.id,sound])

    async_loop = asyncio.new_event_loop()
    outgoing = asyncio.Queue()
    incoming = asyncio.Queue()

    def send(message):
        async def inner_send():
            await outgoing.put(json.dumps(message))
        asyncio.run_coroutine_threadsafe(inner_send(),async_loop)

    def send_and_recieve(message):
        async def inner_loop():
            send(message)
            response = await incoming.get()
            return response
        return asyncio.run_coroutine_threadsafe(inner_loop(),async_loop)


    async def sender(websocket):
        while True:
            message = await outgoing.get()
            await websocket.send(message)

    async def handle_incoming(message, websocket):
        message = json.loads(message)
        if message[0]=="startup":
            global local_keywords
            local_keywords=message[1]
            lowkey = {}
            for i in local_keywords:
                lowkey[int(i)]=local_keywords[i]
            local_keywords=lowkey
        elif message[0]=='response':
            await incoming.put(message[1])

    async def bot_client():
        url = "ws://localhost:2299"
        async with websockets.connect(url) as websocket:
            asyncio.get_running_loop().create_task(sender(websocket))

            while True:
                incoming = await websocket.recv()
                asyncio.run_coroutine_threadsafe(handle_incoming(incoming,websocket),async_loop)

    def start_client():
        async_loop.create_task(bot_client())
        async_loop.run_forever()

    threading.Thread(target=start_client, daemon=True).start()


    api_key = os.getenv("API_KEY")
    bot.run()



main()
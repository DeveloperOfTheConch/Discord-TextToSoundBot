import discord
import asyncio
import websockets
import threading
import json
import os

bot = discord.Bot(intents=discord.Intents.all())

local_keywords = {}

def main():




    @bot.event
    async def on_guild_join(guild):
        send(['addserver',guild.id])

    @bot.event
    async def on_guild_remove(guild):
        send(['removeserver',guild.id])



    @bot.event
    async def on_ready():
        ids = []
        for i in bot.guilds:
            ids.append(i.id)
        send(['startup',ids])
        await asyncio.sleep(3)
        print(f'{bot.user} is now online')


    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        keywords = local_keywords[message.guild.id]
        if message.content in keywords:
            send(["playsound",message.content])


    @bot.slash_command(description="Add a sound: /addsound <keyword> <link>")
    async def addsound(ctx, keyword, link):
        if len(keyword)>32:
            await ctx.respond("Keyword cannot be longer than 32 characters!")
            return
        if keyword in local_keywords[ctx.guild.id]:
            await ctx.respond(f'{keyword} is already a keyword!')
            return
        send(["addsound",keyword,link])
        await ctx.respond(f"New sound added with keyword {keyword} successfully.")
        local_keywords[ctx.guild.id].append(keyword)


    @bot.slash_command(description="Remove a sound: /removesound <keyword>")
    async def removesound(ctx, keyword):
        if keyword not in local_keywords[ctx.guild.id]:
            ctx.respond(f'{keyword} is not an established keyword.')
            return
        send(["removesound",keyword])
        await ctx.respond(f'Sound with keyword {keyword} removed.')
        local_keywords[ctx.guild.id].remove(keyword)



    async_loop = asyncio.new_event_loop()
    outgoing = asyncio.Queue()

    def send(message):
        async def innerSend():
            data = json.dumps(['b',message])
            await outgoing.put(data)
        asyncio.run_coroutine_threadsafe(innerSend(),async_loop)


    async def sender(websocket):
        while True:
            message = await outgoing.get()
            await websocket.send(message)

    async def handleIncoming(message, websocket):
        if message[0]=="startup":
            global local_keywords
            local_keywords=message[1]

    async def botClient():
        url = "ws://localhost:2288"
        async with websockets.connect(url) as websocket:
            asyncio.get_running_loop().create_task(sender(websocket))

            while True:
                incoming = await websocket.recv()
                asyncio.run_coroutine_threadsafe(handleIncoming(incoming,websocket),async_loop)

    def startClient():
        async_loop.create_task(botClient())
        async_loop.run_forever()

    threading.Thread(target=startClient, daemon=True).start()


    api_key = os.getenv("API_KEY")
    bot.run(api_key)



main()
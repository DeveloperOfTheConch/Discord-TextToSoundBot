import asyncio
import websockets
import time

async def server(websocket):
    async for message in websocket:
        print(f'Recieved: {message}')
        print("sending...")
        await websocket.send(f"You sent: {message}")
        print("sent!")


async def main():
    async with websockets.serve(server, "localhost",2288):
        print("Server running")
        await asyncio.Future()

asyncio.run(main())
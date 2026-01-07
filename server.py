import asyncio
import websockets


async def server(websocket):
    async for message in websocket:
        print(f'Recieved: {message}')
        await websocket.send(f"You sent: {message}")


async def main():
    async with websockets.serve(server, "localhost",2288):
        print("Server running")
        await asyncio.Future()

asyncio.run(main())
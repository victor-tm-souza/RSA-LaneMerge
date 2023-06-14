import asyncio
import websockets
from websockets.server import serve

# Maintain a list of connected clients
connected_clients = set()


async def handle_message(message, sender):
    # Forward the message to all other connected clients
    for client in connected_clients:
        if client != sender:
            await client.send(message)


async def server(websocket, path):
    # Add the client to the connected clients set
    connected_clients.add(websocket)

    try:
        async for message in websocket:
            print(message)
            await handle_message(message, websocket)
    finally:
        # Remove the client from the connected clients set
        connected_clients.remove(websocket)


async def main():
    async with serve(server, "localhost", 7555):
        await asyncio.Future()

asyncio.run(main())

# WS server example

import asyncio
import websockets


async def receive(websocket, path):
    data = await websocket.recv()
    if len(data)>1:
        print(f"< {data}")

start_server = websockets.serve(receive, "localhost", 5000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

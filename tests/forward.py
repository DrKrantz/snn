import asyncio
from subprocess import Popen, PIPE
import websockets


class ScreenParser:
    def __init__(self, script_name, send_cb):
        self.recorder = Popen(['python', script_name], stdout=PIPE)
        self.__send_cb = send_cb

    def run(self):
        while True:
            out = self.recorder.stdout.readline()
            if out:
                self.__send_cb(out.decode())


async def forward_ws(msg):
    uri = "ws://localhost:5000"
    async with websockets.connect(uri) as websocket:
        await websocket.send(msg)


loop = asyncio.get_event_loop()


def message_handler(msg):
    loop.run_until_complete(forward_ws(msg))


if __name__ == '__main__':
    parser = ScreenParser('write_to_screen.py', message_handler)
    parser.run()

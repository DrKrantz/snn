import asyncio
from subprocess import Popen, PIPE
import websockets


loop = asyncio.get_event_loop()


class ScreenParser:
    def __init__(self, script_name, send_cb):
        self.recorder = Popen(['python', script_name], stdout=PIPE)
        self.__send_cb = send_cb

    def run(self):
        while True:
            out = self.recorder.stdout.readline()
            if out:
                self.__send_cb(out.decode())


class MessageHandler:
    uri = "ws://localhost:5000"

    def __init__(self):
        self.__ws = websockets.connect(self.uri)

    async def send(self, msg):
        async with self.__ws as ws:
            await ws.send(msg)

    def handle(self, msg):
        loop.run_until_complete(self.send(msg))


if __name__ == '__main__':
    handler = MessageHandler()
    parser = ScreenParser('write_to_screen.py', handler.handle)
    parser.run()

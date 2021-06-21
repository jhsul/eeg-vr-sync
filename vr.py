import asyncio
import concurrent
import re

import websockets



class VRParser:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.df = None
        self.done = False
        self.server = None

    async def handler(self, websocket, path):
        while not self.done:
            message = await websocket.recv()

            message = re.sub(r'[^\x00-\x7f]',r'', message)
            message = re.sub(r'[\u0000-\u0019]+',r'', message)
            print(message)

    def run_server(self):
        self.server = websockets.serve(self.handler, self.host, self.port)
        return self.server
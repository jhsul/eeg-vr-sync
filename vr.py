import asyncio
import concurrent
import re

import websockets

from datetime import datetime as dt


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
            self.server.ws_server.close()
            #print(dir(self.server.ws_server))
            self.done = True
            if self.event_loop is not None:
                self.event_loop.stop()


    def start_server(self):
        print(f"[{dt.now()}] Starting websocket server on ws://{self.host}:{self.port}")
        self.server = websockets.serve(self.handler, self.host, self.port)

        return self.server

import asyncio
import concurrent

import websockets



class VRParser:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.df = None
        self.done = False
        self.server = None

    async def receive_data(self, websocket, path):
        msg = await websocket.recv()
        print(msg)

    def parse_data(self):

        if self.server is None:
            self.server = websockets.serve(self.receive_data, self.host, self.port)

        self.server.wait_closed()
        return self.df

    def get_data(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.parse_data)
            return future
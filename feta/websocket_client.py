#!/usr/bin/env python

import asyncio
import logging

import websockets
from pydantic import BaseModel
from websockets import exceptions

from config import load_config
from constants import CONFIG_PATH
from dependencies import _context, get_host_and_token

# create logger
logging.basicConfig()
logger = logging.getLogger("websocket.client")
logging.root.setLevel(logging.NOTSET)

# the principal registry
config = load_config(CONFIG_PATH)


class WebSocketRequest(BaseModel):
    status: int
    endpoint: str
    data: str
    description: str


async def connect_to_host():
    # todo: auth with dht that you own principal
    host_token = await get_host_and_token(config)

    ws_host = host_token.host.replace("http", "ws", 1)
    host_url = f"{ws_host}/{_context.principal.id}/?token={host_token.token}"
    logger.debug(f"Connecting to: '{host_url}'")
    async with websockets.connect(host_url) as websocket:
        # syn_req = WebSocketRequest(status=1, endpoint="syn", data={"message": "SYN"}, description="greeting")
        await websocket.send("ready!")

        while True:
            try:
                message = await websocket.recv()
                print(f"Host: {message}")

                await websocket.send("response!")

            except exceptions.ConnectionClosedError as e:
                logger.debug(f"Error: {e}")
                logger.info('Reconnecting...')
                # websocket = await websockets.connect(host_url)
            break


if __name__ == '__main__':
    asyncio.run(connect_to_host())

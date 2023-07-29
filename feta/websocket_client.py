#!/usr/bin/env python
import asyncio
import logging

import websockets
from websockets import exceptions

from feta.config import load_config
from feta.constants import CONFIG_PATH
from feta.dependencies import _context
from feta.utils import auth

# create logger
logging.basicConfig()
logger = logging.getLogger("websocket.client")
logging.root.setLevel(logging.NOTSET)

# the principal registry
config = load_config(CONFIG_PATH)


async def connect_to_host():
    # todo: auth with dht that you own principal
    host, token = auth(config.registry_url, config.public_key, config.private_key)
    ws_host = host.replace("http", "ws", 1)
    # headers = {}
    headers = {"Authorization": f"Bearer {token}"}

    host_url = f"{ws_host}/{_context.principal.id}/"
    logger.debug(f"Connecting to: '{host_url}'")
    async with websockets.connect(host_url, extra_headers=headers) as websocket:
        await websocket.send('{"d": "Hello world!"}')

        try:
            message = await websocket.recv()
            logger.debug(f"Received: {message}")

        except exceptions.ConnectionClosedError as e:
            logger.debug(f"Error: {e}")
            logger.info('Reconnecting...')
            websocket = await websockets.connect(host_url)


if __name__ == '__main__':
    asyncio.run(connect_to_host())

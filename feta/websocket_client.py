#!/usr/bin/env python
import logging

from websockets.sync.client import connect

from feta.config import load_config
from feta.constants import CONFIG_PATH
from feta.dependencies import _context
from feta.registry import Registry

# create logger
logging.basicConfig()
logger = logging.getLogger("websocket.client")
logging.root.setLevel(logging.NOTSET)

# the principal registry
registry = Registry(load_config(CONFIG_PATH).registry_url)


def connect_to_host():
    # todo: auth with dht that you own principal
    token = registry.auth(_context.principal.id, "")
    host = registry.sign_on(token, _context.principal.id)

    logger.debug(f"Connecting to: {host}")
    with connect(host) as websocket:
        websocket.send("Hello world!")
        message = websocket.recv()
        logger.debug(f"Received: {message}")


if __name__ == '__main__':
    connect_to_host()

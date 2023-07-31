#!/usr/bin/env python

import asyncio

from websocket_client import connect_to_host

if __name__ == '__main__':
    asyncio.run(connect_to_host())

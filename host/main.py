#!/usr/bin/env python

import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from pydantic import BaseModel


class Event(BaseModel):
    status: int
    data: str
    message: str


# async def handler(websocket):
#     async for message in websocket:
#         event = Event(**json.loads(message))
#         print(event)
#
#
# async def main():
#     async with websockets.serve(handler, "", 9500):
#         await asyncio.Future()  # run forever


app = FastAPI(title="Feta Host")


# todo: load public key for token verification. keys may be rotated daily


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_event(event: Event, websocket: WebSocket):
        await websocket.send_text(event.json())


manager = ConnectionManager()


@app.get("/ping")
async def ping():
    return "pong"


@app.get("/")
async def home():
    response = RedirectResponse(url='/docs')
    return response


@app.websocket("/ws/{principal}")
async def websocket_endpoint(websocket: WebSocket, principal: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            event = Event(**data)
            new_event = Event(status=1, message="", data=json.dumps({"text": f"You wrote: {event}"}))
            await manager.send_event(new_event, websocket)
            print(f"Principal #{principal} says: {event}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # todo: tell registry to remove principal.
        #  registry pings current host and realise connections is no longer valiid then disconnests

# if __name__ == "__main__":
#     asyncio.run(main())

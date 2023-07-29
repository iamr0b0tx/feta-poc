#!/usr/bin/env python
import binascii
import json
import logging
from base64 import b64encode, b64decode

import jwt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import RedirectResponse

from schemas import AuthRequest, Response, Event
from utils import get_derived_key, KeyPair, generate_token, decode_token

signing_key_pair = KeyPair.generate_key_pair()

logger = logging.getLogger(__name__)
logging.basicConfig()
logging.root.setLevel(logging.NOTSET)

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
        await websocket.send_json(event.json())


manager = ConnectionManager()


@app.get("/ping")
async def ping():
    return "pong"


@app.get("/")
async def home():
    response = RedirectResponse(url='/docs')
    return response


@app.get("/principal/")
async def get_public_key():
    return Response(
        status=1,
        data={
            "principal": b64encode(signing_key_pair.get_public_key()),
            "iat": signing_key_pair.iat
        },
        message=""
    )


@app.post("/auth/")
async def auth(auth_request: AuthRequest):
    try:
        peer_public_key = b64decode(auth_request.principal)
        derived_key = get_derived_key(peer_public_key, signing_key_pair.private_key)
        decode_token(auth_request.token, derived_key)

        # todo: prefer to just use private signing key like so
        # signing_key_pair.private_key.private_bytes(
        #     encoding=serialization.Encoding.PEM,
        #     format=serialization.PrivateFormat.PKCS12,
        #     encryption_algorithm=serialization.NoEncryption()
        # )
        token = generate_token(derived_key, peer_public_key.decode("utf-8"))
        return Response(status=1, data={"token": token}, message="")

    except jwt.exceptions.DecodeError as e:
        logger.debug(str(e))
        raise HTTPException(status_code=400, detail="Invalid token")

    except binascii.Error as e:
        logger.debug(str(e))
        raise HTTPException(status_code=400, detail="Invalid public key")


@app.websocket("/ws/{principal}/")
async def websocket_endpoint(websocket: WebSocket, principal: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive()
            print(data)
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

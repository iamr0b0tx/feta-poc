#!/usr/bin/env python

import binascii
import logging
from base64 import b64decode

import jwt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi import status
from fastapi.exceptions import WebSocketException
from fastapi.responses import RedirectResponse

from connection_manager import ConnectionManager
from dependencies import get_signing_key_pair, JWTBearer
from schemas import AuthRequest, Response, WebSocketRequest
from utils import get_derived_key, generate_token, decode_token, KeyPair

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


# todo: load public key for token verification. keys may be rotated daily
app = FastAPI(title="Feta Host")

# todo: Adding the CORS middleware to the app
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

manager = ConnectionManager()


@app.get("/ping")
async def ping():
    return "pong"


@app.get("/")
async def home():
    response = RedirectResponse(url='/docs')
    return response


@app.get("/principal/")
async def get_principal(signing_key_pair: KeyPair = Depends(get_signing_key_pair)):
    return Response(
        status=1,
        data={
            "principal": signing_key_pair.get_public_key_b64(),
            "iat": signing_key_pair.iat
        },
        message=""
    )


@app.get("/principals/{principal}", dependencies=[Depends(JWTBearer())])
async def get_principal_metadata(principal: str):
    return Response(
        status=1,
        data={
            "metadata": 99,
            "principal": principal
        },
        message=""
    )


@app.post("/auth/")
async def auth(auth_request: AuthRequest, signing_key_pair: KeyPair = Depends(get_signing_key_pair)):
    try:
        peer_public_key = b64decode(auth_request.principal)
        derived_key = get_derived_key(peer_public_key, signing_key_pair.private_key)
        decode_token(auth_request.token, derived_key)

        # todo: prefer to just use private signing key like so
        token = generate_token(signing_key_pair.get_private_key_hash(), peer_public_key.decode("utf-8"))
        return Response(status=1, data={"token": token}, message="")

    except jwt.exceptions.DecodeError as e:
        logger.debug(str(e))
        raise HTTPException(status_code=400, detail="Invalid token")

    except binascii.Error as e:
        logger.debug(str(e))
        raise HTTPException(status_code=400, detail="Invalid public key")


@app.websocket("/ws/{principal}/")
async def websocket_endpoint(websocket: WebSocket, principal: str, token: str):
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    try:
        decode_token(token, get_signing_key_pair().get_private_key_hash())

    except jwt.exceptions.DecodeError as e:
        logger.debug(str(e))
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    await manager.connect(websocket)

    try:
        data = await websocket.receive()
        print(f"Principal #{principal} says: {data}")

        while True:
            req = WebSocketRequest(endpoint="syn", body={"param1": "val1"})
            await manager.send_request(req, websocket)

            data = await websocket.receive()
            print(f"Principal #{principal} says: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # todo: tell registry to remove principal.
        #  registry pings current host and realise connections is no longer valiid then disconnests

# if __name__ == "__main__":
#     asyncio.run(main())

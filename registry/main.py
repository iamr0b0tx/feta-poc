import binascii
import logging
from base64 import b64decode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse

from db import DB, InvalidPublicKey
from registry.utils import KeyPair, validate_host, decode_token, generate_token
from schemas import Host, Response, Token, PrincipalHost
from storage import store

logger = logging.getLogger(__name__)
logging.basicConfig()
logging.root.setLevel(logging.NOTSET)

app = FastAPI(title="Feta Registry")


def get_key_pair():
    return KeyPair.generate_key_pair()


def get_db():
    return DB(store)


@app.get("/")
async def home():
    response = RedirectResponse(url='/docs')
    return response


@app.post("/host/register/")
async def register_host(host: Host, db: DB = Depends(get_db)):
    host_url = validate_host(host.url)
    db.register_host(host_url)
    return Response(status=1, data={}, message="")


@app.post("/token/verify/")
async def verify_token(token: Token, key_pair: KeyPair = get_key_pair()):
    # verify token
    try:
        data = decode_token(token.token, key_pair.public_key)
        return Response(status=1, data=data, message="")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/principal/host/")
async def get_principal_host(principal_host: PrincipalHost, db: DB = Depends(get_db),
                             key_pair: KeyPair = get_key_pair()):
    # todo: authenticate principal
    try:
        db.sync_principal_public_key(principal_host.principal, principal_host.public_key)
    except InvalidPublicKey as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        peer_public_key: EllipticCurvePublicKey = serialization.load_ssh_public_key(
            b64decode(principal_host.public_key),
            backend=default_backend())
        shared_key = key_pair.private_key.exchange(ec.ECDH(), peer_public_key)
        print(shared_key)
        token = generate_token(shared_key, principal_host.principal)
        return Response(
            status=1,
            data={
                "host": db.get_host(principal_host.principal),
                "token": token
            },
            message=""
        )
    except binascii.Error as e:
        logger.debug(str(e))
        raise HTTPException(status_code=400, detail="Invalid Public Key")


@app.get("/public-key/")
async def get_public_key(key_pair: KeyPair = get_key_pair()):
    return Response(
        status=1,
        data={
            "key": key_pair.get_public_key(),
            "iat": key_pair.iat
        },
        message=""
    )


@app.get("/ping")
async def ping():
    return "pong"

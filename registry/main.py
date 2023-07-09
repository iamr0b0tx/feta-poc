import binascii
import logging
from base64 import b64encode

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse

from db import DB, InvalidPublicKey
from schemas import Host, Response, Token, PrincipalHost
from storage import store
from utils import KeyPair, validate_host, decode_token, generate_token, get_derived_key

logger = logging.getLogger(__name__)
logging.basicConfig()
logging.root.setLevel(logging.NOTSET)

app = FastAPI(title="Feta Registry")
signing_key_pair = KeyPair.generate_key_pair()
encryption_key_pair = KeyPair.generate_key_pair()


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
async def verify_token(token: Token):
    try:
        derived_key = get_derived_key(token.public_key, signing_key_pair.private_key)
        data = decode_token(token.token, derived_key)
        return Response(status=1, data=data, message="")

    except binascii.Error as e:
        logger.debug(str(e))
        raise HTTPException(status_code=400, detail="Invalid Public key")


@app.post("/principal/host/")
async def get_principal_host(principal_host: PrincipalHost, db: DB = Depends(get_db)):
    # todo: authenticate principal
    try:
        db.sync_principal_public_key(principal_host.principal, principal_host.public_key)
    except InvalidPublicKey as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        derived_key = get_derived_key(principal_host.public_key, signing_key_pair.private_key)
        token = generate_token(derived_key, principal_host.principal)
        return Response(
            status=1,
            data={
                "host": db.get_host(principal_host.principal),
                "public_key": b64encode(signing_key_pair.get_public_key()),
                "iat": signing_key_pair.iat
            },
            message=""
        )
    except binascii.Error as e:
        logger.debug(str(e))
        raise HTTPException(status_code=400, detail="Invalid Public Key")


@app.get("/ping")
async def ping():
    return "pong"

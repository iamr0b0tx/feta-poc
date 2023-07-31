import binascii
import logging

import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse

from dependencies import get_store, get_signing_key_pair
from key_pair import KeyPair
from schemas import AddPrincipalRequestBody, CreateTokenRequestBody, Response
from storage.storage import Storage
from utils import principal_to_public_key, get_derived_key, decode_token, generate_token

logger = logging.getLogger(__name__)
logging.basicConfig()
logging.root.setLevel(logging.NOTSET)

app = FastAPI(title="Feta")


@app.get("/ping")
async def ping():
    return "pong"


@app.get("/")
async def home():
    response = RedirectResponse(url='/docs')
    return response


@app.post("/principals/")
async def add_principal(add_principal_request_body: AddPrincipalRequestBody,
                        store: Storage = Depends(get_store), signing_key_pair: KeyPair = Depends(get_signing_key_pair)):
    try:
        public_key = principal_to_public_key(add_principal_request_body.principal)
        derived_key = get_derived_key(public_key, signing_key_pair.private_key)
        decode_token(add_principal_request_body.token, derived_key)
        store.add_principal(add_principal_request_body.principal)
        return Response(status=1, data={}, detail="")

    except jwt.exceptions.DecodeError as e:
        logger.debug(str(e))
        raise HTTPException(status_code=400, detail="Invalid token")

    except binascii.Error as e:
        logger.debug(str(e))
        raise HTTPException(status_code=400, detail="Invalid public key")


@app.post("/tokens/")
async def create_token(create_token_request_body: CreateTokenRequestBody,
                       signing_key_pair: KeyPair = Depends(get_signing_key_pair)):
    try:
        public_key = principal_to_public_key(create_token_request_body.principal)
        derived_key = get_derived_key(public_key, signing_key_pair.private_key)
        decode_token(create_token_request_body.token, derived_key)

        # todo: prefer to just use private signing key
        token = generate_token(signing_key_pair.get_private_key_hash(), public_key)
        return Response(status=1, data={"token": token}, detail="")

    except jwt.exceptions.DecodeError as e:
        logger.debug(str(e))
        raise HTTPException(status_code=400, detail="Invalid token")

    except binascii.Error as e:
        logger.debug(str(e))
        raise HTTPException(status_code=400, detail="Invalid public key")

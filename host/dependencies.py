import logging

import jwt
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from utils import KeyPair, decode_token

logger = logging.getLogger(__name__)
logging.basicConfig()
logging.root.setLevel(logging.NOTSET)

_signing_key_pair = None


def get_signing_key_pair():
    global _signing_key_pair
    if _signing_key_pair is None:
        _signing_key_pair = KeyPair.generate_key_pair()
    return _signing_key_pair


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")

            return credentials.credentials

        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    @staticmethod
    def verify_jwt(token: str) -> bool:
        is_token_valid: bool = False

        try:
            payload = decode_token(token, get_signing_key_pair().get_private_key_hash())
        except jwt.exceptions.DecodeError as e:
            logger.debug(str(e))
            payload = None

        if payload:
            is_token_valid = True

        return is_token_valid

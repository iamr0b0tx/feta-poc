import logging

from fastapi import HTTPException, Depends

from constants import PUBLIC_KEY, PRIVATE_KEY, REGISTRY_URL
from exceptions import NoAvailableHost, AuthenticationError
from key_pair import KeyPair
from storage import make_storage
from utils import authenticate

logger = logging.getLogger(__name__)
logging.basicConfig()
logging.root.setLevel(logging.NOTSET)

_host_token = None
_store = None
_signing_key_pair = None


async def get_store():
    global _store
    if _store is None:
        _store = make_storage()
    return _store


async def get_signing_key_pair():
    global _signing_key_pair
    if _signing_key_pair is None:
        _signing_key_pair = KeyPair.generate_key_pair()
    return _signing_key_pair


async def get_host_and_token():
    global _host_token
    if _host_token is None:
        try:
            _host_token = authenticate(REGISTRY_URL, PUBLIC_KEY, PRIVATE_KEY)

        except NoAvailableHost as e:
            logger.error(f"no available host: {e}")
            raise HTTPException(status_code=404, detail="no available host")

        except AuthenticationError as e:
            logger.error(f"could not authenticate: {e}")
            raise HTTPException(status_code=404, detail="could not authenticate")

    return _host_token

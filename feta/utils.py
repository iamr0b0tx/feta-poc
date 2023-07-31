import json
import logging
from base64 import b64decode, b64encode
from datetime import timezone, datetime, timedelta

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey, EllipticCurvePrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from pydantic import BaseModel

from constants import JWT_ALGORITHM, ENCODING, TOKEN_LIFETIME_SECONDS
from exceptions import NoAvailableHost, AuthenticationError

# create logger
logging.basicConfig()
logger = logging.getLogger("websocket.client")
logging.root.setLevel(logging.NOTSET)


class HostToken(BaseModel):
    host: str
    token: str
    exp: str


def authenticate(url, public_key: EllipticCurvePublicKey,
                 private_key: EllipticCurvePrivateKey) -> HostToken:
    try:
        response = requests.get(f"{url}/hosts/random")
        logger.debug(response.content)
        if response.status_code == 404:
            raise NoAvailableHost()
        host = response.json()["data"]["host"]

        response = requests.get(f"{host}/principal/")
        logger.debug(response.content)
        host_public_key = response.json()["data"]["principal"]

        host_public_key: EllipticCurvePublicKey = serialization.load_ssh_public_key(
            b64decode(host_public_key),
            backend=default_backend())
        # source: https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ec/#elliptic-curve-key-exchange-algorithm
        shared_key = private_key.exchange(ec.ECDH(), host_public_key)
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
        ).derive(shared_key)

        public_key = public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        )
        public_key = b64encode(public_key).decode("utf-8")
        now = datetime.now(tz=timezone.utc)
        token = jwt.encode(
            {
                "public_key": public_key,
                "iat": now,
                "exp": now + timedelta(minutes=5)
            },
            derived_key,
            algorithm=JWT_ALGORITHM
        )

        response = requests.post(
            f"{host}/auth/",
            json={
                "token": token,
                "principal": public_key
            }
        )
        token = response.json()["data"]["token"]
        host = f"{host}/ws"

        return HostToken(
            host=host,
            token=token,
            exp=jwt.decode(token, options={"verify_signature": False})["exp"]
        )

    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"could not authenticate: {e}")
        raise AuthenticationError()


def public_key_to_principal(public_key: bytes) -> str:
    return b64encode(public_key).decode(ENCODING)


def principal_to_public_key(principal: str) -> bytes:
    return b64decode(principal)


def create_config(config, path):
    with open(path, 'w') as f:
        json.dump(config, f)


def make_principal(principal, path):
    with open(path, 'w') as f:
        json.dump(principal, f)


def get_derived_key(peer_public_key, private_key):
    peer_public_key: EllipticCurvePublicKey = serialization.load_ssh_public_key(
        peer_public_key,
        backend=default_backend())
    shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
    ).derive(shared_key)


def decode_token(token, key):
    return jwt.decode(
        token,
        key,
        algorithms=[JWT_ALGORITHM],
        options={
            "require": ["exp"],
            "verify_exp": True,
            "verify_signature": True
        }
    )


def generate_token(key, principal, algo=JWT_ALGORITHM):
    now = datetime.now(tz=timezone.utc)
    return jwt.encode(
        {
            "principal": principal,
            "iat": now,
            "exp": now + timedelta(seconds=TOKEN_LIFETIME_SECONDS)
        },
        key,
        algorithm=algo
    )

import logging
from base64 import b64decode, b64encode
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Set

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey, EllipticCurvePrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from constants import JWT_ALGORITHM, AUTHENTICATION_TOKEN_LIFETIME_MINUTES, LEEWAY_SECONDS

# create logger
logging.basicConfig()
logger = logging.getLogger("websocket.client")
logging.root.setLevel(logging.NOTSET)


class PublicKeyLoadError(Exception):
    def __init__(self, message="Could not get latest public key"):
        super().__init__(message)


class AuthenticationError(Exception):
    def __init__(self, message="Could not authenticate"):
        super().__init__(message)


class RegistrationError(Exception):
    def __init__(self, message="Could not register principal"):
        super().__init__(message)


class BlockNotFound(Exception):
    def __init__(self, tags: Set[str], message="Could not find block with tags: {}"):
        super().__init__(message.format(tags))


class AddBlockError(Exception):
    def __init__(self, block, tags: Set[str], message="error adding block '{}' with tags {}"):
        super().__init__(message.format(block, tags))


class GetAllBlocksError(Exception):
    def __init__(self, message="error getting all blocks"):
        super().__init__(message)


class AuthorizationError(Exception):
    def __init__(self, message="you are not authorized to make this request. token not provided or expired"):
        super().__init__(message)


@dataclass
class PublicKey:
    public_key: Optional[EllipticCurvePublicKey]
    iat: datetime
    exp: datetime


@dataclass
class Token:
    principal: str
    iat: datetime
    exp: datetime
    token: str

    @classmethod
    def from_token(cls, token: str):
        payload = jwt.decode(token, options={"verify_signature": False})
        return Token(
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
            principal=payload["principal"],
            token=token
        )


def try_(func, new_token):
    def wrap():
        try:
            func()
        except AuthorizationError:
            new_token()
            func()

    return wrap


class FetaClient:
    def __init__(self, url: str, public_key: EllipticCurvePublicKey, private_key: EllipticCurvePrivateKey):
        self.__public_key = PublicKey(
            public_key=None,
            exp=datetime.fromtimestamp(0, tz=timezone.utc),
            iat=datetime.fromtimestamp(0, tz=timezone.utc),
        )

        self.__url = url
        self.__private_key = private_key
        self.__principal = b64encode(
            public_key.public_bytes(
                serialization.Encoding.OpenSSH,
                serialization.PublicFormat.OpenSSH
            )
        ).decode("UTF-8")

        self.__register()
        self.__authenticate()

    @property
    def principal(self):
        return self.__principal

    # todo: create a safe equivalent like safe_add, safe_get that can detect authorization error and refresh token
    def add(self, data: str, tags: Set[str]):
        response = requests.post(
            f"{self.__url}/blocks/",
            json={"tags": list(tags), "data": data},
            headers={"Authorization": f"Bearer: {self.__get_latest_token().token}"}
        )

        if response.status_code == 403:
            return AuthorizationError()

        if response.status_code != 200:
            raise AddBlockError(data, tags)

        logger.debug(response.content)
        data = response.json()["data"]
        return data

    def get(self, tags: Set[str]):
        response = requests.get(
            f"{self.__url}/blocks/",
            params={"tags": ",".join(map(str, tags))},
            headers={"Authorization": f"Bearer: {self.__get_latest_token().token}"}
        )

        if response.status_code != 200:
            raise BlockNotFound(tags)

        if response.status_code == 403:
            return AuthorizationError()

        logger.debug(response.content)
        data = response.json()["data"]
        return data

    def get_all(self):
        response = requests.get(
            f"{self.__url}/blocks/all",
            headers={"Authorization": f"Bearer: {self.__get_latest_token().token}"}
        )

        if response.status_code != 200:
            raise GetAllBlocksError()

        if response.status_code == 403:
            return AuthorizationError()

        logger.debug(response.content)
        data = response.json()["data"]
        return data

    def __get_latest_token(self):
        if self.__token.exp < (datetime.now(tz=timezone.utc) - timedelta(seconds=LEEWAY_SECONDS)):
            self.__authenticate()

        return self.__token

    def __get_latest_public_key(self) -> PublicKey:
        if self.__public_key.exp > (datetime.now(tz=timezone.utc) + timedelta(seconds=LEEWAY_SECONDS)):
            return self.__public_key

        try:
            response = requests.get(f"{self.__url}/principal/")
            logger.debug(response.content)
            data = response.json()["data"]

            self.__public_key = PublicKey(
                iat=datetime.fromtimestamp(data["iat"], tz=timezone.utc),
                exp=datetime.fromtimestamp(data["exp"], tz=timezone.utc),
                public_key=serialization.load_ssh_public_key(
                    b64decode(data["principal"]),
                    backend=default_backend()
                )
            )

            return self.__public_key

        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"could not authenticate: {e}")
            raise PublicKeyLoadError()

    def __get_authentication_token(self) -> str:
        # source:
        # https://cryptography.io/en/latest/hazat/primitives/asymmetric/ec/#elliptic-curve-key-exchange-algorithm
        feta_public_key = self.__get_latest_public_key()
        shared_key = self.__private_key.exchange(ec.ECDH(), feta_public_key.public_key)

        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
        ).derive(shared_key)

        now = datetime.now(tz=timezone.utc)
        return jwt.encode(
            {
                "principal": self.__principal,
                "iat": now,
                "exp": now + timedelta(minutes=AUTHENTICATION_TOKEN_LIFETIME_MINUTES)
            },
            derived_key,
            algorithm=JWT_ALGORITHM
        )

    def __authenticate(self):
        try:
            authentication_token = self.__get_authentication_token()
            response = requests.post(
                f"{self.__url}/tokens/",
                json={
                    "token": authentication_token,
                    "principal": self.__principal
                }
            )

            logger.debug(response.content)
            self.__token = Token.from_token(response.json()["data"]["token"])

        except (requests.exceptions.JSONDecodeError, PublicKeyLoadError) as e:
            logger.error(f"could not authenticate: {e}")
            raise AuthenticationError()

    def __register(self):
        try:
            authentication_token = self.__get_authentication_token()
            response = requests.post(
                f"{self.__url}/principals/",
                json={
                    "token": authentication_token,
                    "principal": self.__principal
                }
            )

            logger.debug(response.content)
            if response.status_code != 200:
                RegistrationError(f"unable to register principal: {response.content}")

        except (requests.exceptions.JSONDecodeError, PublicKeyLoadError) as e:
            logger.error(f"could not authenticate: {e}")
            raise RegistrationError()

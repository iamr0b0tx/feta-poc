from base64 import b64decode
from dataclasses import dataclass
from json import load
from os.path import exists

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey, EllipticCurvePublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey

from feta.constants import ENCODING


class ConfigNotFound(Exception):
    def __init__(self, *, path=None, message="block not found"):
        if path:
            message = f"config '{path}' not found"

        super().__init__(message)


@dataclass
class Config:
    principal_path: str
    registry_url: str  # url type or ipv4
    private_key: EllipticCurvePrivateKey  # url type or ipv4
    public_key: EllipticCurvePublicKey  # url type or ipv4


def load_config(path) -> Config:
    # TODO: revisit this exception
    if not exists(path):
        raise ConfigNotFound(path=path)

    with open(path, "r", encoding=ENCODING) as file:
        data = load(file)

        private_key = b64decode(data["private_key"].encode())
        public_key = b64decode(data["public_key"].encode())

        public_key = serialization.load_ssh_public_key(public_key, backend=default_backend())
        private_key = serialization.load_pem_private_key(private_key, None, backend=default_backend())

        data["private_key"] = private_key
        data["public_key"] = public_key
        return Config(**data)

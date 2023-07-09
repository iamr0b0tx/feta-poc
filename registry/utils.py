from base64 import b64decode
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization, serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey, EllipticCurvePrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

JWT_ALGORITHM = "HS256"


def validate_host(host):
    # todo: check if is valid ipv4/v6 or domain
    # if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host):
    #     raise HTTPException(status_code=400, detail="Invalid Host: Host must be IPv4 address")
    return host


def generate_token(key, principal):
    now = datetime.now(tz=timezone.utc)
    return jwt.encode(
        {
            "principal": principal,
            "iat": now,
            "exp": now + timedelta(minutes=5)
        },
        key,
        algorithm=JWT_ALGORITHM
    )


@dataclass
class KeyPair:
    # todo: rotate key pairs at least daily
    private_key: EllipticCurvePrivateKey
    public_key: EllipticCurvePublicKey
    iat: datetime

    def get_public_key(self):
        # source: https://stackoverflow.com/a/39126754/8927391
        return self.public_key.public_bytes(
            crypto_serialization.Encoding.OpenSSH,
            crypto_serialization.PublicFormat.OpenSSH
        )

    @classmethod
    def generate_key_pair(cls) -> 'KeyPair':
        private_key = ec.generate_private_key(ec.SECP384R1())
        return KeyPair(
            private_key=private_key,
            public_key=private_key.public_key(),
            iat=datetime.now(tz=timezone.utc)
        )


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


def get_derived_key(peer_public_key, private_key):
    peer_public_key: EllipticCurvePublicKey = serialization.load_ssh_public_key(
        b64decode(peer_public_key),
        backend=default_backend())
    shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
    ).derive(shared_key)


def auth():
    pass

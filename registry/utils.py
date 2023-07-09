from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

import jwt
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey, EllipticCurvePrivateKey


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
        algorithm="HS256"
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


def decode_token(token, public_key):
    return jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        options={
            "require": ["exp"],
            "verify_exp": True,
            "verify_signature": True
        }
    )


def auth():
    pass

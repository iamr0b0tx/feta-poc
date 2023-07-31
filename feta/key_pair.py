import hashlib
from base64 import b64encode
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey, EllipticCurvePublicKey

from constants import KEYPAIR_LIFETIME_SECONDS


@dataclass
class KeyPair:
    # todo: rotate key pairs at least daily
    private_key: EllipticCurvePrivateKey
    public_key: EllipticCurvePublicKey
    iat: datetime
    exp: datetime

    def get_public_key(self):
        # source: https://stackoverflow.com/a/39126754/8927391
        return self.public_key.public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        )

    def get_public_key_b64(self):
        return b64encode(self.get_public_key())

    @classmethod
    def generate_key_pair(cls) -> 'KeyPair':
        private_key = ec.generate_private_key(ec.SECP384R1())
        return KeyPair(
            private_key=private_key,
            public_key=private_key.public_key(),
            iat=datetime.now(tz=timezone.utc),
            exp=datetime.now(tz=timezone.utc) + timedelta(seconds=KEYPAIR_LIFETIME_SECONDS)
        )

    def get_private_key_hash(self):
        return hashlib.new(
            'sha256',
            self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        ).hexdigest().encode("utf-8")

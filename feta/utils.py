from base64 import b64decode, b64encode
from datetime import timezone, datetime, timedelta
from typing import Tuple

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey, EllipticCurvePrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from feta.constants import JWT_ALGORITHM


def auth(url, principal: str, public_key: EllipticCurvePublicKey,
         private_key: EllipticCurvePrivateKey) -> Tuple[str, str]:
    public_key = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )
    public_key = b64encode(public_key).decode("utf-8")

    response = requests.post(
        f"{url}/principal/host/",
        json={"principal": principal, "public_key": public_key}
    )

    data = response.json()["data"]
    host = data["host"]

    server_public_key: EllipticCurvePublicKey = serialization.load_ssh_public_key(
        b64decode(data["public_key"]),
        backend=default_backend())
    shared_key = private_key.exchange(ec.ECDH(), server_public_key)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
    ).derive(shared_key)

    now = datetime.now(tz=timezone.utc)
    token = jwt.encode(
        {
            "principal": principal,
            "iat": now,
            "exp": now + timedelta(minutes=5)
        },
        derived_key,
        algorithm=JWT_ALGORITHM
    )

    return host, token

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


def auth(url, public_key: EllipticCurvePublicKey,
         private_key: EllipticCurvePrivateKey) -> Tuple[str, str]:
    response = requests.get(f"{url}/hosts/")
    host = response.json()["data"]["host"]

    response = requests.get(f"{host}/principal/")
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

    return host, token

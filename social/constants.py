import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey, EllipticCurvePrivateKey


def load_private_key(path, password) -> EllipticCurvePrivateKey:
    with open(path, "rb") as file:
        return serialization.load_pem_private_key(file.read(), password, backend=default_backend())


def load_public_key(path) -> EllipticCurvePublicKey:
    with open(path, "rb") as file:
        return serialization.load_ssh_public_key(file.read(), backend=default_backend())


WORKING_DIR = os.environ["WORKING_DIR"]
FETA_URL = os.environ["FETA_URL"]
PRIVATE_KEY = load_private_key(os.environ["PRIVATE_KEY_FILE_PATH"], os.environ.get("PRIVATE_KEY_PASSWORD"))
PUBLIC_KEY = load_public_key(os.environ["PUBLIC_KEY_FILE_PATH"])
APP_NAME = "Social"
JWT_ALGORITHM = "HS256"
AUTHENTICATION_TOKEN_LIFETIME_MINUTES = 1
LEEWAY_SECONDS = 0

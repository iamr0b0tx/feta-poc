import secrets
from json import load
from os.path import exists

from pydantic import BaseModel

from feta.constants import ENCODING


class Principal(BaseModel):
    id: str
    metadata: dict


def create_principal(path) -> Principal:
    principal = Principal(id=secrets.token_hex(16), metadata="{}")
    save_principal(path, principal)
    return principal


def save_principal(path, principal):
    with open(path, "w", encoding=ENCODING) as file:
        file.write(principal.json())


def load_principal(path: str) -> Principal:
    if not exists(path):
        return create_principal(path)

    # TODO: principal should be encrypted
    with open(path, "r", encoding=ENCODING) as file:
        return Principal(**load(file))


def update_metadata(path: str, metadata: dict):
    principal = load_principal(path)
    principal.metadata.update(metadata)
    principal = Principal(id=principal.id, metadata=principal.metadata)
    save_principal(path, principal)
    return principal

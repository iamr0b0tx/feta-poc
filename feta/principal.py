from json import load
from os.path import exists

from pydantic import BaseModel

from constants import ENCODING


class Principal(BaseModel):
    id: str
    metadata: dict


def load_contributor_principal(path: str, principal: Principal) -> Principal:
    if exists(path):
        return load_principal(path)

    principal = Principal(id=principal.id, metadata={})
    save_principal(path, principal)
    return principal


def save_principal(path, principal, force=False):
    if (not force) and exists(path):
        return

    with open(path, "w", encoding=ENCODING) as file:
        file.write(principal.json())


def load_principal(path: str) -> Principal:
    # TODO: principal should be encrypted
    with open(path, "r", encoding=ENCODING) as file:
        return Principal(**load(file))


def update_metadata(path: str, metadata: dict):
    principal = load_principal(path)
    principal.metadata.update(metadata)

    principal = Principal(id=principal.id, metadata=principal.metadata)
    save_principal(path, principal, force=True)

    return principal

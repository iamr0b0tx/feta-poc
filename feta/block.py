import hashlib
from json import load
from os.path import exists
from typing import Optional

from pydantic import BaseModel

from feta.constants import ENCODING


class Block(BaseModel):
    id: str
    data: str
    principal: str
    contributor: str

    @property
    def key(self):
        return get_block_key(self.id, self.contributor)


class BlockNotFound(Exception):
    def __init__(self, *, idx=None, message="block not found"):
        if idx:
            message = f"block '{idx}' not found"

        super().__init__(message)


def create_block(data: str, principal: str, contributor: str):
    return Block(
        id=hashlib.new('sha256', data.encode(ENCODING)).hexdigest(),
        data=data, principal=principal, contributor=contributor
    )


def get_block_key(idx, contributor):
    return idx, contributor


def load_block(path: str) -> Optional[Block]:
    if not exists(path):
        return

    with open(path, "r", encoding=ENCODING) as file:
        return Block(**load(file))

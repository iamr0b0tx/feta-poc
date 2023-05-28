import hashlib
from json import load
from os.path import exists, join
from typing import Optional

from pydantic import BaseModel

from feta.constants import ENCODING


class Block(BaseModel):
    id: str
    data: str
    principal: str
    contributor: str


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


def save_block(working_dir: str, block: Block, contributor: str):
    path = join(working_dir, contributor, block.id)
    with open(path, "w", encoding=ENCODING) as file:
        file.write(block.json())


def load_block(path: str) -> Optional[Block]:
    if not exists(path):
        return

    with open(path, "r", encoding=ENCODING) as file:
        return Block(**load(file))

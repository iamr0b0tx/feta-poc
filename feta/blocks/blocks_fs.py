from collections import OrderedDict
from json import load
from os import unlink
from os.path import join, exists, dirname
from typing import TypeVar, Optional

from block import Block, get_block_key, BlockNotFound
from blocks.blocks_base import BlocksBase
from config import Config
from constants import ENCODING

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


def load_block(path: str) -> Optional[Block]:
    if not exists(path):
        return

    with open(path, "r", encoding=ENCODING) as file:
        return Block(**load(file))


class LRUCache:
    # source: https://www.geeksforgeeks.org/lru-cache-in-python-using-ordereddict/
    # initialising capacity
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    # we return the value of the key
    # that is queried in O(1) and return -1 if we
    # don't find the key in out dict / cache.
    # And also move the key to the end
    # to show that it was recently used.
    def get(self, key: _KT) -> int:
        if key not in self.cache:
            return -1
        else:
            self.cache.move_to_end(key)
            return self.cache[key]

    # first, we add / update the key by conventional methods.
    # And also move the key to the end to show that it was recently used.
    # But here we will also check whether the length of our
    # ordered dictionary has exceeded our capacity,
    # If so we remove the first key (least recently used)
    def put(self, key: _KT, value: _VT) -> None:
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def pop(self, key: _KT):
        self.cache.pop(key)


class BlocksFS(BlocksBase):
    # todo: consider using sqlite db
    def __init__(self, config: Config):
        super().__init__(config)

        self.__working_dir = dirname(config.principal_path)

        # blocks cache
        self.__blocks = LRUCache(50)

    @property
    def working_dir(self):
        return self.__working_dir

    def __get_block_path(self, idx, contributor):
        return join(self.__working_dir, contributor, idx)

    def create_block(self, data: str, contributor):
        block = super().make_block(data, contributor)

        path = join(self.__working_dir, contributor, block.id)
        with open(path, "w", encoding=ENCODING) as file:
            file.write(block.json())

        self.__blocks.put(block.key, block)
        return block

    def __load_block(self, idx: str, contributor) -> Optional[Block]:
        block = load_block(self.__get_block_path(idx, contributor))
        if block and block.id == idx and block.contributor == contributor:
            return block

    def __delete_block(self, idx: str, contributor: str):
        path = self.__get_block_path(idx, contributor)
        unlink(path)

    def retrieve_block(self, idx, contributor):
        # TODO: verify block with blocks DHT?
        block = self.__blocks.get(get_block_key(idx, contributor))
        if block != -1:
            return block

        block = self.__load_block(idx, contributor)
        if block is not None:
            return block

        raise BlockNotFound(idx=idx)

    def destroy_block(self, idx, contributor):
        # TODO: remove block from blocks DHT?
        path = self.__get_block_path(idx, contributor)
        if not exists(path):
            raise BlockNotFound(idx=idx)

        self.__delete_block(idx, contributor)
        self.__blocks.pop(get_block_key(idx, contributor))

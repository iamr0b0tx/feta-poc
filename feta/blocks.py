from collections import OrderedDict
from os import unlink
from os.path import dirname, join, exists
from typing import TypeVar, Optional

from feta.block import Block, create_block, save_block, load_block, get_block_key, BlockNotFound
from feta.config import load_config
from feta.principal import load_principal

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


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


class Blocks:
    def __init__(self, config_path: str):
        config = load_config(config_path)
        self.__working_dir = dirname(config.principal_path)

        self.__principal = load_principal(config.principal_path)

        # blocks memory
        self.__blocks = LRUCache(50)

    @property
    def principal(self):
        return self.__principal

    @property
    def working_dir(self):
        return self.__working_dir

    def __get_block_path(self, idx, contributor):
        return join(self.__working_dir, contributor, idx)

    def create_block(self, data: str, contributor):
        block = create_block(data=data, principal=self.__principal.id, contributor=contributor)

        # TODO: store block in blocks DHT
        save_block(self.__working_dir, block, contributor)

        self.__blocks.put(get_block_key(block.id, contributor), block)
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

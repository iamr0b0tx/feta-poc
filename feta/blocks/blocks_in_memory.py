from block import Block
from blocks.blocks_base import BlocksBase
from config import Config


class BlocksInMemory(BlocksBase):
    def __init__(self, config: Config):
        super().__init__(config)
        self.__data = {}

    def create_block(self, data: str, contributor) -> Block:
        block = super().make_block(data, contributor)
        self.__data[block.key] = block
        return block

    def retrieve_block(self, idx, contributor) -> Block:
        return self.__data.get(self.get_block_key(idx, contributor))

    def destroy_block(self, idx, contributor) -> None:
        block_key = self.get_block_key(idx, contributor)
        if block_key in self.__data:
            del self.__data[block_key]


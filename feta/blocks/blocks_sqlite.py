from feta.block import Block
from feta.blocks.blocks_base import BlocksBase


class BlocksSqlite(BlocksBase):
    def create_block(self, data: str, contributor) -> Block:
        pass

    def retrieve_block(self, idx, contributor) -> Block:
        pass

    def destroy_block(self, idx, contributor) -> None:
        pass

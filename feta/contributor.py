from os import mkdir
from os.path import join, exists

from feta.blocks import Blocks


class Contributor:
    def __init__(self, blocks: Blocks, contributor_principal: str):
        self.__blocks = blocks
        self.__id = self.__load_contributor(contributor_principal)

    @property
    def blocks(self):
        return self.__blocks

    @property
    def id(self):
        return self.__id

    def __load_contributor(self, contributor_principal: str) -> str:
        # TODO: principal should exist in marketplace DHT
        assert contributor_principal is not None

        path = join(self.__blocks.working_dir, contributor_principal)
        if not exists(path):
            mkdir(path)

        return contributor_principal

    def create_block(self, data: str):
        return self.__blocks.create_block(data, self.__id)

    def retrieve_block(self, idx: str):
        return self.__blocks.retrieve_block(idx, self.__id)

    def destroy_block(self, idx: str):
        return self.__blocks.destroy_block(idx, self.__id)

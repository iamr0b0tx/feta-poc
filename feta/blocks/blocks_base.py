from abc import abstractmethod

from feta.block import Block, create_block, get_block_key
from feta.config import Config
from feta.principal import load_principal


class BlocksBase:
    def __init__(self, config: Config):
        self.get_block_key = get_block_key
        self.__principal = load_principal(config.principal_path)

    @property
    def principal(self):
        return self.__principal

    def make_block(self, data: str, contributor):
        block = create_block(data=data, principal=self.__principal.id, contributor=contributor)
        # TODO: store block in blocks DHT
        return block

    @abstractmethod
    def create_block(self, data: str, contributor) -> Block:
        pass

    @abstractmethod
    def retrieve_block(self, idx, contributor) -> Block:
        pass

    @abstractmethod
    def destroy_block(self, idx, contributor) -> None:
        pass

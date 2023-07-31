from os.path import dirname

from blocks import Blocks
from blocks.blocks_base import BlocksBase
from config import load_config
from peers import Peers
from principal import load_principal


class Context:
    def __init__(self, config_path: str):
        config = load_config(config_path)
        self.__working_dir = dirname(config.principal_path)
        self.__principal = load_principal(config.principal_path)

        self.__blocks: BlocksBase = Blocks(config)
        self.__peers = Peers()

    @property
    def peers(self):
        return self.__peers

    @property
    def principal(self):
        return self.__principal

    @property
    def working_dir(self):
        return self.__working_dir

    @property
    def blocks(self):
        return self.__blocks

    @property
    def peers(self):
        return self.__peers

from feta.blocks import Blocks
from feta.constants import CONFIG_PATH

_blocks = None


async def get_blocks():
    global _blocks
    if _blocks is None:
        _blocks = Blocks(CONFIG_PATH)
    return _blocks

from feta.constants import CONFIG_PATH
from feta.context import Context

_context = Context(CONFIG_PATH)


async def get_context():
    global _context
    if _context is None:
        _context = Context(CONFIG_PATH)
    return _context

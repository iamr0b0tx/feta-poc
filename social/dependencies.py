from fastapi import Depends

from feta.blocks import Blocks
from feta.contributor import Contributor
from feta.dependencies import get_blocks
from social.constants import PRINCIPAL
from social.post_manager import PostManager

_contributor = None


def get_contributor(blocks: Blocks = Depends(get_blocks)):
    global _contributor
    if _contributor is None:
        _contributor = Contributor(blocks, PRINCIPAL)
    return _contributor


_post_manager = None


def get_post_manager(contributor: Contributor = Depends(get_contributor)):
    global _post_manager
    if _post_manager is None:
        _post_manager = PostManager(contributor)
    return _post_manager

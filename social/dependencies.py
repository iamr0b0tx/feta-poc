from fastapi import Depends

from context import Context
from contributor import Contributor
from dependencies import get_context
from social.constants import PRINCIPAL
from social.managers.posts import PostManager
from social.managers.users import UserManager

_contributor = None


def get_contributor(context: Context = Depends(get_context)):
    global _contributor
    if _contributor is None:
        _contributor = Contributor(context, PRINCIPAL)
    return _contributor


_post_manager = None


def get_post_manager(contributor: Contributor = Depends(get_contributor)):
    global _post_manager
    if _post_manager is None:
        _post_manager = PostManager(contributor)
    return _post_manager


_user_manager = None


def get_user_manager(contributor: Contributor = Depends(get_contributor)):
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager(contributor)
    return _user_manager

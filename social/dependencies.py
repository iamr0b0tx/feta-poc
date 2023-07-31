from fastapi import Depends

from constants import FETA_URL, PUBLIC_KEY, PRIVATE_KEY
from feta_client import FetaClient
from managers.posts import PostManager
from managers.users import UserManager

_feta_client = None
_post_manager = None


def get_feta_client():
    global _feta_client
    if _feta_client is None:
        _feta_client = FetaClient(FETA_URL, PUBLIC_KEY, PRIVATE_KEY)
    return _feta_client


def get_post_manager(feta_client: FetaClient = Depends(get_feta_client)):
    global _post_manager
    if _post_manager is None:
        _post_manager = PostManager(feta_client)
    return _post_manager


_user_manager = None


def get_user_manager(feta_client: FetaClient = Depends(get_feta_client)):
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager(feta_client)
    return _user_manager

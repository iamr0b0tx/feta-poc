from fastapi import Depends

from feta.router import make_router
from social.constants import PRINCIPAL, PRINCIPAL_NAME
from social.dependencies import get_post_manager
from social.post_manager import PostManager

router = make_router(PRINCIPAL, PRINCIPAL_NAME, "posts")


@router.get("/{post_id}")
async def get_post(post_id: str, post_manager: PostManager = Depends(get_post_manager)):
    return post_manager.get_post(post_id)


@router.post("/")
async def create_post(text: str, post_manager: PostManager = Depends(get_post_manager)):
    return post_manager.create_post(text)

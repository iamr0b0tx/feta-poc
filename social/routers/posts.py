from fastapi import Depends, APIRouter

from constants import APP_NAME
from dependencies import get_post_manager
from managers.posts import PostManager

router = APIRouter(
    prefix=f"/{APP_NAME}/posts",
    tags=[f"{APP_NAME} / posts"],
    responses={404: {"detail": "Not found"}}
)


@router.get("/{post_id}")
async def get_post(post_id: str, post_manager: PostManager = Depends(get_post_manager)):
    try:
        return post_manager.get_post(post_id)
    except:
        pass


@router.post("/")
async def create_post(text: str, post_manager: PostManager = Depends(get_post_manager)):
    return post_manager.create_post(text)

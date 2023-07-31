from fastapi import Depends, HTTPException

from router import make_router
from social.constants import PRINCIPAL, PRINCIPAL_NAME
from social.dependencies import get_user_manager
from social.managers.users import UserManager, UserNotFound

router = make_router(PRINCIPAL, PRINCIPAL_NAME, "users")


@router.post("/sign-up")
async def sign_up(username: str, user_manager: UserManager = Depends(get_user_manager)):
    return user_manager.sign_up(username)


@router.get("/profile")
async def get_profile(user_manager: UserManager = Depends(get_user_manager)):
    try:
        return user_manager.get_profile()
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/profile/{principal}")
async def get_user_profile(principal: str, user_manager: UserManager = Depends(get_user_manager)):
    try:
        return user_manager.get_user_profile(principal)
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

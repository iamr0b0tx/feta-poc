from fastapi import Depends, HTTPException, APIRouter

from constants import APP_NAME
from dependencies import get_user_manager
from managers.users import UserManager, ProfileNotFound
from routers.users import UpdateProfileRequestBody

router = APIRouter(
    prefix=f"/{APP_NAME}/profile",
    tags=[f"{APP_NAME} / profile"],
    responses={404: {"detail": "Not found"}}
)


@router.get("/")
async def get_profile(user_manager: UserManager = Depends(get_user_manager)):
    try:
        return user_manager.get_profile()
    except ProfileNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/")
async def update_profile(update_profile_request_body: UpdateProfileRequestBody,
                         user_manager: UserManager = Depends(get_user_manager)):
    return user_manager.sign_up(update_profile_request_body)

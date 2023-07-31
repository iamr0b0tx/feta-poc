from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel

from constants import APP_NAME
from dependencies import get_user_manager
from managers.users import UserManager, UserNotFound

router = APIRouter(
    prefix=f"/{APP_NAME}/users",
    tags=[f"{APP_NAME} / users"],
    responses={404: {"detail": "Not found"}}
)


class UpdateProfileRequestBody(BaseModel):
    username: str




@router.get("/{principal}/")
async def get_user(principal: str, user_manager: UserManager = Depends(get_user_manager)):
    try:
        return user_manager.get_user_profile(principal)
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

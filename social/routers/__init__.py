from fastapi import APIRouter

from social.routers import posts, users

router = APIRouter()
router.include_router(posts.router)
router.include_router(users.router)

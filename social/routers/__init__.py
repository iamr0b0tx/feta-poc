from fastapi import APIRouter

from social.routers import posts

router = APIRouter()
router.include_router(posts.router)

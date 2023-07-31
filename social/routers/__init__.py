from fastapi import APIRouter

from routers import posts, users, profile

router = APIRouter()
router.include_router(posts.router)
router.include_router(users.router)
router.include_router(profile.router)

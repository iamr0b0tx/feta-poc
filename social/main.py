from fastapi import FastAPI

from feta.router import router as main_router
from social.routers import router as social_router

app = FastAPI()
app.include_router(main_router)
app.include_router(social_router)


@app.get("/ping")
async def ping():
    return "pong"

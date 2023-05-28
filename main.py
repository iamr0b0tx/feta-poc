from fastapi import FastAPI

from notes.router import router as notes_router
from social.routers import router as social_router

app = FastAPI()
app.include_router(notes_router)
app.include_router(social_router)


@app.get("/ping")
async def ping():
    return "pong"

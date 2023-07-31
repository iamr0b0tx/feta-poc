from fastapi import FastAPI

from routers import router as social_router

app = FastAPI(title="Social")
app.include_router(social_router)


@app.get("/ping")
async def ping():
    return "pong"

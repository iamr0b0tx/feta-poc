from fastapi import FastAPI

from router import router as main_router
from notes.router import router as notes_router

app = FastAPI()
app.include_router(main_router)
app.include_router(notes_router)


@app.get("/ping")
async def ping():
    return "pong"

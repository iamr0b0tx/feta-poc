from fastapi import FastAPI

from feta.router import router

app = FastAPI()
app.include_router(router)


@app.get("/ping")
async def ping():
    return "pong"

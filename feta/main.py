from fastapi import FastAPI

from feta.dependencies import _context
from feta.registry import Registry
from feta.router import router

app = FastAPI()
app.include_router(router)

registry = Registry()


def connect_to_host():
    # todo: auth with dht that you own principal
    token = registry.auth(_context.principal, "")
    registry.sign_on(token, _context.principal)


@app.get("/ping")
async def ping():
    return "pong"

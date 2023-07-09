import re

from fastapi import FastAPI, Depends, HTTPException

from db import DB
from storage import store

app = FastAPI()


def get_db():
    return DB(store)


def validate_host(host):
    # toto: check if is valid ipv4/v6 or domain
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host):
        raise HTTPException(status_code=400, detail="Invalid Host: Host must be IPv4 address")
    return host


@app.post("/register/host/{host}")
async def register_host(host: str, db: DB = Depends(get_db)):
    host = validate_host(host)
    db.register_host(host)
    return ""


@app.get("/principal/host/")
async def get_principal_host(principal: str, db: DB = Depends(get_db)):
    return db.get_host(principal)


@app.get("/ping")
async def ping():
    return "pong"

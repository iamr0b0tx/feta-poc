from pydantic import BaseModel


class AuthRequest(BaseModel):
    principal: str
    token: str


class Response(BaseModel):
    status: int
    data: dict
    message: str


class Event(BaseModel):
    status: int
    data: str
    message: str

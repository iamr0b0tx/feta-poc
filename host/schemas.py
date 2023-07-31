from pydantic import BaseModel


class AuthRequest(BaseModel):
    principal: str
    token: str


class Response(BaseModel):
    status: int
    data: dict
    message: str


class WebSocketRequest(BaseModel):
    endpoint: str
    body: dict

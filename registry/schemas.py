from pydantic import BaseModel


class Token(BaseModel):
    token: str
    public_key: str


class Host(BaseModel):
    url: str


class PrincipalHost(BaseModel):
    principal: str
    public_key: str


class Response(BaseModel):
    status: int
    data: dict
    message: str

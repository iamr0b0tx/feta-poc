from pydantic import BaseModel


class AddPrincipalRequestBody(BaseModel):
    principal: str
    token: str


class CreateTokenRequestBody(BaseModel):
    principal: str
    token: str


class Response(BaseModel):
    status: int
    data: dict
    detail: str

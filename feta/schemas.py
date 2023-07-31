from typing import Union, List

from pydantic import BaseModel


class AddPrincipalRequestBody(BaseModel):
    principal: str
    token: str


class CreateTokenRequestBody(BaseModel):
    principal: str
    token: str


class GetAllBlocksRequestBody(BaseModel):
    token: str


class AddBlockRequestBody(BaseModel):
    tags: List[str]
    data: str


class Response(BaseModel):
    status: int
    data: Union[dict, list]
    detail: str

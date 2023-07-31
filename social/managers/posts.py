import time

from pydantic import BaseModel

from feta_client import FetaClient


class Post(BaseModel):
    text: str
    timestamp: int


class PostManager:
    def __init__(self, feta_client: FetaClient):
        self.__feta_client = feta_client

    def create_post(self, text):
        post = Post(text=text, timestamp=time.time_ns())
        return self.__feta_client.blocks.create_block(post.json(), self.__feta_client.id)

    def get_post(self, idx):
        return self.__feta_client.blocks.retrieve_block(idx, self.__feta_client.id)

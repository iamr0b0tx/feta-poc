import time

from pydantic import BaseModel

from contributor import Contributor


class Post(BaseModel):
    text: str
    timestamp: int


class PostManager:
    def __init__(self, contributor: Contributor):
        self.__contributor = contributor

    def create_post(self, text):
        post = Post(text=text, timestamp=time.time_ns())
        return self.__contributor.blocks.create_block(post.json(), self.__contributor.id)

    def get_post(self, idx):
        return self.__contributor.blocks.retrieve_block(idx, self.__contributor.id)

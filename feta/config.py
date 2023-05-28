from json import load
from os.path import exists

from pydantic import BaseModel

from feta.constants import ENCODING


class ConfigNotFound(Exception):
    def __init__(self, *, path=None, message="block not found"):
        if path:
            message = f"config '{path}' not found"

        super().__init__(message)


class Config(BaseModel):
    principal_path: str


def load_config(path):
    # TODO: revisit this exception
    if not exists(path):
        raise ConfigNotFound(path=path)

    with open(path, "r", encoding=ENCODING) as file:
        data = load(file)
        return Config(principal_path=data["principal"])

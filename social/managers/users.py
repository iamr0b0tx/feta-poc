import json

from pydantic import BaseModel

from feta_client import FetaClient


class User(BaseModel):
    username: str


class UserNotFound(Exception):
    def __init__(self, *, principal=None, message="User not found"):
        if principal:
            message = f"User '{principal}' not found"
        super().__init__(message)


class ProfileNotFound(Exception):
    def __init__(self, *, principal=None, message="Profile not found"):
        if principal:
            message = f"'{principal}' profile not found"
        super().__init__(message)


class UserManager:
    def __init__(self, feta_client: FetaClient):
        self.__feta_client = feta_client
        self.__principal = feta_client.principal

    def sign_up(self, data):
        # TODO: check if username unique
        user = User(username=data.username)
        self.__feta_client.add(user.json(), {self.__principal})
        return user

    def get_user_profile(self, principal: str):
        results = self.__feta_client.get({principal})

        if not results:
            raise UserNotFound(principal=principal)

        return User(**json.loads(results[0]))

    def get_profile(self):
        results = self.__feta_client.get({self.__principal})

        if not results:
            raise ProfileNotFound(principal=self.__principal)

        return User(**json.loads(results[0]))

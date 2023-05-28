from pydantic import BaseModel, ValidationError

from feta.contributor import Contributor, PrincipalNotFound


class User(BaseModel):
    username: str


class UserNotFound(Exception):
    def __init__(self, *, principal=None, message="User not found"):
        if principal:
            message = f"User '{principal}' not found"
        super().__init__(message)


class UserManager:
    def __init__(self, contributor: Contributor):
        self.__contributor = contributor
        self.__blocks = self.__contributor.blocks

    def sign_up(self, username):
        # TODO: check if username unique
        user = User(username=username)
        metadata = self.__contributor.update_metadata(user.dict())
        return User(**metadata)

    def get_user_profile(self, principal: str):
        try:
            metadata = self.__contributor.get_metadata(principal)
            return User(**metadata)
        except (PrincipalNotFound, ValidationError):
            raise UserNotFound(principal=principal)

    def get_profile(self):
        principal = self.__contributor.principal.id

        try:
            metadata = self.__contributor.get_metadata(principal)
            return User(**metadata)
        except (PrincipalNotFound, ValidationError):
            raise UserNotFound(principal=principal)

from os import mkdir
from os.path import join, exists

from feta.context import Context
from feta.principal import update_metadata, load_contributor_principal


class PrincipalNotFound(Exception):
    def __init__(self, *, principal=None, message="Principal not found"):
        if principal:
            message = f"Principal '{principal}' not found"
        super().__init__(message)


class Contributor:
    def __init__(self, context: Context, contributor_principal: str):
        # todo: change blocks to context to hold blocks and peers
        self.__context = context
        self.__id = self.__load_contributor(contributor_principal)

        self.__principal_path = join(self.__context.working_dir, self.__id, "principal")
        self.__principal = load_contributor_principal(self.__principal_path, self.__context.principal)

    @property
    def context(self):
        # todo: return only contributor related blocks
        return self.__context

    @property
    def id(self):
        return self.__id

    @property
    def principal(self):
        return self.__principal

    def __load_contributor(self, contributor_principal: str) -> str:
        # TODO: principal should exist in marketplace DHT
        assert contributor_principal is not None

        path = join(self.__context.working_dir, contributor_principal)
        if not exists(path):
            mkdir(path)

        return contributor_principal

    def create_block(self, data: str):
        return self.__blocks.create_block(data, self.__id)

    def retrieve_block(self, idx: str):
        return self.__blocks.retrieve_block(idx, self.__id)

    def destroy_block(self, idx: str):
        return self.__blocks.destroy_block(idx, self.__id)

    def update_metadata(self, metadata):
        self.__principal = update_metadata(self.__principal_path, metadata)
        return self.__principal.metadata

    def get_metadata(self, principal: str):
        # TODO: make request to principal DHT to get user data
        if principal == self.__principal.id:
            return self.__principal.metadata

        raise PrincipalNotFound(principal=principal)

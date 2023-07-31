from storage.storage import Storage


class InMemoryStorage(Storage):
    def __init__(self):
        self.__data = {}
        self.__principals = set()

    def add_principal(self, principal: str):
        self.__principals.add(principal)

    def principal_exists(self, principal: str):
        return principal in self.__principals

    def get(self, key: str) -> str:
        return self.__data.get(key)

    def set(self, key: str, value: str):
        self.__data[key] = value

    def pop(self, key: str) -> str:
        return self.__data.pop(key)

    def all(self) -> dict:
        return self.__data.copy()

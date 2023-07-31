from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def add_principal(self, key: str) -> str:
        pass
    @abstractmethod
    def get(self, key: str) -> str:
        pass

    @abstractmethod
    def set(self, key: str, value: str):
        pass

    @abstractmethod
    def pop(self, key: str) -> str:
        pass

    @abstractmethod
    def all(self) -> dict:
        pass

from abc import ABC, abstractmethod


class MessageQueue(ABC):
    @abstractmethod
    def get(self, key: str) -> str:
        pass

    @abstractmethod
    def set(self, key: str, value: str):
        pass

    @abstractmethod
    def pop(self, key: str) -> str:
        pass

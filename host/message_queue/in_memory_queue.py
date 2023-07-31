from message_queue.message_queue import MessageQueue


class InMemoryQueue(MessageQueue):
    def __init__(self):
        self.__data = {}

    def get(self, key: str) -> str:
        return self.__data.get(key)

    def set(self, key: str, value: str):
        self.__data[key] = value

    def pop(self, key: str) -> str:
        return self.__data.pop(key)

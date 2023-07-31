from collections import defaultdict
from typing import Set, List, Dict


class PrincipalSpecificStorage:
    def __init__(self):
        self.__permission_set: Set[str] = set()
        self.__blocks: List[str] = []
        self.__tags = defaultdict(set)

    def add(self, block: str, tags: Set[str]):
        self.__blocks.append(block)
        block_id = len(self.__blocks) - 1

        for tag in tags:
            self.__tags[tag].add(block_id)

    def get(self, tags: Set[str]):
        # todo: needs to support more complicated tag boolean
        result = self.__tags[tags.pop()].copy()
        for tag in tags:
            result.intersection_update(self.__tags[tag])

        # todo: requires some form of pagination, also sorting
        return list(map(lambda i: self.__blocks[i], result))

    def get_all(self):
        return self.__blocks


class InMemoryStorage:
    def __init__(self):
        self.__data: Dict[str, PrincipalSpecificStorage] = {}

    def add_principal(self, principal: str):
        self.__data[principal] = PrincipalSpecificStorage()

    def principal_exists(self, principal: str):
        return principal in self.__data

    def get(self, principal: str, tags: Set[str]) -> List[str]:
        return self.__data[principal].get(tags)

    def add(self, principal: str, block: str, tags: Set[str]):
        self.__data[principal].add(block, tags)

    def get_all(self, principal: str) -> List[str]:
        return self.__data[principal].get_all()

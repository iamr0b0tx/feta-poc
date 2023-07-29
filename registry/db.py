from random import choices
from typing import Union

from storage.storage import Storage

ENCODING = "utf-8"


def host_is_valid(host):
    # todo: ping host to check host is still healthy and valid
    return host


class InvalidPublicKey(Exception):
    def __init__(self, message="The public key provided is not consistent with what was initially registered!"):
        super().__init__(message)


class DB:
    HOSTS_KEY = "hosts"
    PRINCIPAL_HOST_PREFIX = "principal:host:"
    PRINCIPAL_PUBLIC_KEY_PREFIX = "principal:public_key:"

    def __init__(self, store: Storage):
        self.__store = store

    @staticmethod
    def __get_key(prefix: str, principal: str):
        return f"{prefix}{principal}"

    def __get_principal_host_key(self, principal: str):
        return self.__get_key(self.PRINCIPAL_HOST_PREFIX, principal)

    def __get_principal_public_key_key(self, principal: str):
        return self.__get_key(self.PRINCIPAL_PUBLIC_KEY_PREFIX, principal)

    # def sync_principal_public_key(self, principal: str, public_key: str):
    #     # todo: create a way to rotate the key pairs
    #     key = self.__get_principal_public_key_key(principal)
    #     hashed_public_key = self.__store.get(key)
    #     new_hashed_public_key = hashlib.new('sha256', public_key.encode(ENCODING)).hexdigest()
    #     if hashed_public_key is None:
    #         self.__store.set(key, new_hashed_public_key)
    #         return
    #
    #     if hashed_public_key != new_hashed_public_key:
    #         raise InvalidPublicKey()

    def set_principal_host(self, principal: str, host: str) -> str:
        principal_host_key = self.__get_principal_host_key(principal)
        self.__store.set(principal_host_key, host)
        return host

    def get_host(self) -> Union[str, None]:
        # todo: gather list of close hosts and select random one
        hosts = self.__get_hosts()
        if not hosts:
            return None

        host = choices(hosts)[0]
        return host

    # def get_host(self, principal: str) -> str:
    #     # TODO: check if exists, if true verify ownership of principal if not then tell principal has been used
    #     principal_host_key = self.__get_principal_host_key(principal)
    #
    #     current_host = self.__store.get(principal_host_key)
    #     if host_is_valid(current_host):
    #         return current_host
    #
    #     # todo: gather list of close hosts and select random one
    #     host = choices(self.__get_hosts())[0]
    #     self.__store.set(principal_host_key, host)
    #     return host

    def register_host(self, host):
        hosts = self.__get_hosts()
        hosts.append(host)
        self.__store.set(self.HOSTS_KEY, ",".join(hosts))

    def __get_hosts(self):
        hosts = self.__store.get(self.HOSTS_KEY)
        if hosts is None:
            return []
        return hosts.split(",")

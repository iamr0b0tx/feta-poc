from random import choices

from storage.storage import Storage


def host_is_valid(host):
    # todo: ping host to check host is still healthy and valid
    return host


class DB:
    HOSTS_KEY = "hosts"
    PRINCIPAL_PREFIX = "principal:"

    def __init__(self, store: Storage):
        self.__store = store

    def __get_principal_key(self, principal: str):
        return f"{self.PRINCIPAL_PREFIX}{principal}"

    def get_host(self, principal: str) -> str:
        # TODO: check if exists, if true verify ownership of principal if not then tell principal has been used
        principal_key = self.__get_principal_key(principal)

        current_host = self.__store.get(principal_key)
        if host_is_valid(current_host):
            return current_host

        # todo: gather list of close hosts and select random one
        host = choices(self.__get_hosts())[0]
        self.__store.set(principal_key, host)
        return host

    def register_host(self, host):
        hosts = self.__get_hosts()
        hosts.append(host)
        self.__store.set(self.HOSTS_KEY, ",".join(hosts))

    def __get_hosts(self):
        hosts = self.__store.get(self.HOSTS_KEY) or ""
        return hosts.split(",")

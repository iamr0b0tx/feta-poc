import requests


class Registry:
    def __init__(self, registry_url):
        self.__url = registry_url
        self.__token = None

    def auth(self, principal: str, public_key: str) -> str:
        response = requests.post(f"{self.__url}/principal/host/", json={"principal": principal})
        print(response.content)
        self.__token = ""
        return ""

    def sign_on(self, token: str, principal: str) -> str:
        requests.post(self.__url, )
        return ""

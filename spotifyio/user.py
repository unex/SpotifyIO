from typing import List

from .http import HTTPClient
from .asset import Asset
from .mixins import Url


class User(Url):
    __slots__ = (
        "id",
        "uri",
        "external_urls",
        "display_name",
        "followers",
        "images",
    )

    def __init__(self, http: HTTPClient, data: dict) -> None:
        self._http = http

        self.id: str = data["id"]
        self.uri: str = data["uri"]
        self.external_urls: dict = data["external_urls"]
        self.display_name: str = data["display_name"]
        self.followers: int = data["followers"]["total"]
        self.images: List[Asset] = [Asset(**a) for a in data["images"]]


class ClientUser(User):
    __slots__ = ()


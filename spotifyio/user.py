from typing import List

from .http import HTTPClient
from .asset import Asset


class User:
    def __init__(self, http: HTTPClient, data: dict) -> None:
        self._http = http

        self.display_name: str = data.pop("display_name")
        self.external_urls: dict = data.pop("external_urls")
        self.followers: int = data.pop("followers").get("total")
        self.url: str = data.pop("href")
        self.id: str = data.pop("id")
        self.images: List[Asset] = [Asset(**a) for a in data.pop("images")]
        self.uri: str = data.pop("uri")


class ClientUser(User):
    pass

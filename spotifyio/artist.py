from typing import List

from .http import HTTPClient
from .asset import Asset
from .mixins import Url


class PartialArtist(Url):
    __slots__ = (
        "id",
        "uri",
        "external_urls",
        "name",
    )

    def __init__(self, http: HTTPClient, data: dict) -> None:
        self._http = http

        self.id: str = data["id"]
        self.uri: str = data["uri"]
        self.external_urls: dict = data["external_urls"]
        self.name: str = data["name"]


class Artist(Url):
    __slots__ = (
        "id",
        "uri",
        "external_urls",
        "name",
        "followers",
        "genres",
        "images",
        "popularity",
    )

    def __init__(self, http: HTTPClient, data: dict) -> None:
        self._http = http

        self.id: str = data["id"]
        self.uri: str = data["uri"]
        self.external_urls: dict = data["external_urls"]
        self.name: str = data["name"]
        self.followers: int = data["followers"]["total"]
        self.genres: List[str] = data["genres"]
        self.images: List[Asset] = [Asset(**a) for a in data["images"]]
        self.popularity: int = data["popularity"]

    def __repr__(self) -> str:
        attrs = " ".join(f"{name}={getattr(self, name)}" for name in ["id", "name"])
        return f"<{self.__class__.__qualname__} {attrs}>"

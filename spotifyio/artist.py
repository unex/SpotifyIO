from typing import TYPE_CHECKING, List

from .asset import Asset
from .mixins import Url

if TYPE_CHECKING:
    from .state import State


class Artist(Url):
    __slots__ = (
        "_state",
        "id",
        "uri",
        "external_urls",
        "name",
        "followers",
        "genres",
        "images",
        "popularity",
    )

    def __init__(self, state, data: dict) -> None:
        self._state: State = state

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

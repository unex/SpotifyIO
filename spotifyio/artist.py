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

    if TYPE_CHECKING:
        id: str
        uri: str
        external_urls: dict
        name: str
        genres: List[str]
        followers: int
        images: List[Asset]
        popularity: int

    def __init__(self, state, data: dict) -> None:
        self._state: State = state
        self.id = data["id"]
        self.uri = data["uri"]
        self.external_urls = data["external_urls"]
        self.name = data["name"]

        if "followers" in data:
            self.followers = data["followers"]["total"]
        else:
            self.followers = None

        self.genres = data.get("genres")

        if "images" in data:
            self.images = [Asset(**a) for a in data["images"]]
        else:
            self.images = None

        self.popularity = data.get("popularity")

    def __repr__(self) -> str:
        attrs = " ".join(f"{name}={getattr(self, name)}" for name in ["id", "name"])
        return f"<{self.__class__.__qualname__} {attrs}>"

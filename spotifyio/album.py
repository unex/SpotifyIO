from datetime import date
from typing import TYPE_CHECKING, List, Literal

from .asset import Asset
from .mixins import Url

if TYPE_CHECKING:
    from .state import State
    from .artist import Artist
    from .track import Track


__all__ = ("Album",)


class Album(Url):
    __slots__ = (
        "_state",
        "id",
        "uri",
        "external_urls",
        "name",
        "type",
        "tracks",
        "artists",
        "available_markets",
        "images",
        "release_date",
        "total_tracks",
        "copyrights",
        "external_ids",
        "genres",
        "label",
        "popularity",
    )

    if TYPE_CHECKING:
        id: str
        uri: str
        external_urls: dict
        name: str
        type: Literal["album", "single", "compilation"]
        tracks: List[Track]
        artists: List[Artist]
        markets: List[str]
        images: List[Asset]
        release_date: date
        total_tracks: int
        copyrights: List[dict]
        external_ids: dict
        genres: List[str]
        label: str
        popularity: int

    def __init__(self, state, data: dict) -> None:
        self._state: State = state
        self._update(data)

    def _update(self, data: dict):
        self.id = data["id"]
        self.uri = data["uri"]
        self.external_urls = data["external_urls"]
        self.name = data["name"]
        self.type = data["album_type"]
        self.artists = [self._state.artist(a) for a in data["artists"]]
        self.markets = data["available_markets"]
        self.images = [Asset(**a) for a in data["images"]]
        self.release_date = date.fromisoformat(data["release_date"])
        self.total_tracks = data["total_tracks"]

        if "tracks" in data:
            self.tracks = [self._state.track(t) for t in data["tracks"]["items"]]
        else:
            self.tracks = None

        self.copyrights = data.get("copyrights")
        self.external_ids = data.get("external_ids")
        self.genres = data.get("genres")
        self.label = data.get("label")
        self.popularity = data.get("popularity")

    async def fetch(self):
        self._update(await self._state.http.get_album(self.id))

    def __repr__(self) -> str:
        attrs = " ".join(f"{name}={getattr(self, name)}" for name in ["id", "name"])
        return f"<{self.__class__.__qualname__} {attrs}>"

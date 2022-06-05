from datetime import date
from typing import TYPE_CHECKING, List, Literal

from .asset import Asset
from .mixins import Url

from .utils.list_iterator import ListIterator
from .utils.paginator import Paginator

if TYPE_CHECKING:
    from .state import State
    from .artist import Artist
    from .track import Track


__all__ = ("Album",)


class Album(Url):
    __slots__ = (
        "_state",
        "_tracks",
        "id",
        "uri",
        "external_urls",
        "name",
        "type",
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

        # implement custom type for this mayhaps?
        release_date = data["release_date"]
        precis = data["release_date_precision"]
        if precis == "year":
            self.release_date = date.fromisoformat(f"{release_date}-01-01")
        elif precis == "month":
            self.release_date = date.fromisoformat(f"{release_date}-01")
        else:
            self.release_date = date.fromisoformat(release_date)

        self.total_tracks = data["total_tracks"]

        self._tracks = data.get("tracks")
        self.copyrights = data.get("copyrights")
        self.external_ids = data.get("external_ids")
        self.genres = data.get("genres")
        self.label = data.get("label")
        self.popularity = data.get("popularity")

    @property
    def tracks(self) -> ListIterator["Track"]:
        async def gen():
            async for data in Paginator(
                self._state.http.get_album_tracks, self.id, _data=self._tracks
            ):
                yield self._state.track(data)

        return ListIterator(gen())

    async def fetch(self):
        self._update(await self._state.http.get_album(self.id))

    def __repr__(self) -> str:
        attrs = " ".join(f"{name}={getattr(self, name)}" for name in ["id", "name"])
        return f"<{self.__class__.__qualname__} {attrs}>"

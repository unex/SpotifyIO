from typing import TYPE_CHECKING, List, Literal

from .utils.list_iterator import ListIterator
from .utils.paginator import Paginator

from .asset import Asset
from .mixins import Url

if TYPE_CHECKING:
    from .state import State
    from .album import Album
    from .track import Track

__all__ = ("Artist",)


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
        self._update(data)

    def _update(self, data: dict):
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

    def albums(
        self,
        include: List[Literal["album", "single", "appears_on", "compilation"]] = [
            "album",
            "single",
            "appears_on",
            "compilation",
        ],
    ) -> ListIterator["Album"]:
        async def gen():
            async for data in Paginator(
                self._state.http.get_artist_albums, self.id, include=include
            ):
                yield self._state.objectify(data)

        return ListIterator(gen())

    def top_tracks(self, country: str = "US") -> ListIterator["Track"]:
        async def gen():
            for data in await self._state.http.get_artist_top_tracks(
                self.id, country_code=country
            ):
                yield self._state.objectify(data)

        return ListIterator(gen())

    def related(self) -> ListIterator["Artist"]:
        async def gen():
            for data in await self._state.http.get_artist_related(self.id):
                yield self._state.objectify(data)

        return ListIterator(gen())

    async def fetch(self) -> None:
        self._update(await self._state.http.get_artist(self.id))

    def __repr__(self) -> str:
        attrs = " ".join(f"{name}={getattr(self, name)}" for name in ["id", "name"])
        return f"<{self.__class__.__qualname__} {attrs}>"

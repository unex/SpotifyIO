from typing import TYPE_CHECKING, List, Literal

from .asset import Asset
from .iterators import GenericAsyncIterator
from .mixins import Followable, Url
from .types import SpotifyID, SpotifyURI
from .utils.paginator import Paginator

if TYPE_CHECKING:
    from .album import Album
    from .state import State
    from .track import Track
    from .types import ArtistPayload

__all__ = ("Artist",)


class Artist(Url, Followable):
    """A Spotify Artist.

    Attributes:
        id (:class:`str`): The artist’s unique ID.
        uri (:class:`str`): The artist’s Spotify URI.
        external_urls (:class:`dict`): External links to this artist.
        name (:class:`str`): The artist's name.
        followers (:class:`int`): The artist's followers.
        images (List[:class:`Asset`]): Artwork for this artist.
        genres (List[:class:`str`]): List of genres for this artist.
        popularity (:class:`int`): Artist popularity calculated by Spotify.
    """

    __slots__ = (
        "_state",
        "_followers",
        "id",
        "uri",
        "external_urls",
        "name",
        "genres",
        "images",
        "popularity",
    )

    if TYPE_CHECKING:
        id: SpotifyID
        uri: SpotifyURI
        external_urls: dict
        name: str
        genres: List[str]
        images: List[Asset]
        popularity: int

    def __init__(self, state, data: "ArtistPayload") -> None:
        self._state: State = state
        self._update(data)

    def _update(self, data: "ArtistPayload"):
        self.id = data["id"]
        self.uri = data["uri"]
        self.external_urls = data["external_urls"]
        self.name = data["name"]

        self._followers = data.get("followers")
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
    ) -> GenericAsyncIterator["Album"]:
        """An asynchronous iterator for the artist's albums.

        Args:
            include (List[Literal["album", "single", "appears_on", "compilation"]]): the types of albums to return, default returns all.

        Yields:
            :class:`.Album`:.
        """

        async def gen():
            async for data in Paginator(self._state.http.get_artist_albums, self.id, include=include):
                yield self._state.objectify(data)

        return GenericAsyncIterator(gen())

    def top_tracks(self, country: str = "US") -> GenericAsyncIterator["Track"]:
        """An asynchronous iterator for the artist's top tracks.

        Yields:
            :class:`.Track`:.
        """

        async def gen():
            for data in await self._state.http.get_artist_top_tracks(self.id, country_code=country):
                yield self._state.objectify(data)

        return GenericAsyncIterator(gen())

    def related(self) -> GenericAsyncIterator["Artist"]:
        """An asynchronous iterator for related artists.

        Yields:
            :class:`.Artist`:.
        """

        async def gen():
            for data in await self._state.http.get_artist_related(self.id):
                yield self._state.objectify(data)

        return GenericAsyncIterator(gen())

    async def fetch(self) -> None:
        """Updates a partial of this object with all data"""
        self._update(await self._state.http.get_artist(self.id))

    def __repr__(self) -> str:
        attrs = " ".join(f"{name}={getattr(self, name)}" for name in ["id", "name"])
        return f"<{self.__class__.__qualname__} {attrs}>"

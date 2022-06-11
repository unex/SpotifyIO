from datetime import date
from typing import TYPE_CHECKING, List, Literal

from .asset import Asset
from .iterators import GenericAsyncIterator
from .mixins import Url
from .types import SpotifyID, SpotifyURI
from .utils.paginator import Paginator
from .utils.time import fromspotifyiso

if TYPE_CHECKING:
    from .artist import Artist
    from .state import State
    from .track import Track
    from .types import AlbumPayload, ListAlbumPayload


__all__ = ("Album",)


class Album(Url):
    """A Spotify Album.

    Attributes:
        id (:class:`str`): The album’s unique ID.
        uri (:class:`str`): The album’s Spotify URI.
        external_urls (:class:`dict`): External links to this album.
        name (:class:`str`): The album's name.
        type (`Literal["album", "single", "compilation"]`): The type of album.
        artists (List[:class:`.Artist`]): The artists on this album.
        available_markets (List[:class:`str`]): List of countries this album is avaliable in.
        images (List[:class:`Asset`]): Artwork for this album.
        release_date (:class:`datetime`): The date this album was released.
        total_tracks (:class:`int`): Total number of tracks on this album.
        copyrights (:class:`dict`): Copyright information.
        genres (List[:class:`str`]): List of genres for this album.
        label: (:class:`str`): The label this album was published by.
        popularity (:class:`int`): Album popularity calculated by Spotify.
    """

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
        id: SpotifyID
        uri: SpotifyURI
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

    def __init__(self, state, data: "AlbumPayload") -> None:
        self._state: State = state
        self._update(data)

    def _update(self, data: "AlbumPayload"):
        self.id = data["id"]
        self.uri = data["uri"]
        self.external_urls = data["external_urls"]
        self.name = data["name"]
        self.type = data["album_type"]
        self.artists = [self._state.objectify(a) for a in data["artists"]]
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

        self.markets = data.get("available_markets")
        self._tracks = data.get("tracks")
        self.copyrights = data.get("copyrights")
        self.external_ids = data.get("external_ids")
        self.genres = data.get("genres")
        self.label = data.get("label")
        self.popularity = data.get("popularity")

    def tracks(self) -> GenericAsyncIterator["Track"]:
        """An asynchronous iterator for the album Tracks.

        Yields:
            :class:`.Track`:.
        """

        async def gen():
            async for data in Paginator(self._state.http.get_album_tracks, self.id, _data=self._tracks):
                yield self._state.objectify(data)

        return GenericAsyncIterator(gen())

    async def fetch(self) -> None:
        """Updates a partial of this object with all data"""
        self._update(await self._state.http.get_album(self.id))

    def __repr__(self) -> str:
        attrs = " ".join(f"{name}={getattr(self, name)}" for name in ["id", "name"])
        return f"<{self.__class__.__qualname__} {attrs}>"


class ListAlbum(Album):
    __slots__ = ("added_at",)

    def __init__(self, state, data: "ListAlbumPayload") -> None:
        super().__init__(state, data["album"])

        self.added_at = fromspotifyiso(data["added_at"])

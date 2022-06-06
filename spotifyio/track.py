from typing import TYPE_CHECKING, List

from .mixins import Url
from .types import SpotifyID, SpotifyURI
from .utils.time import fromspotifyiso

if TYPE_CHECKING:
    from .album import Album
    from .artist import Artist
    from .state import State
    from .types import ListTrackPayload, TrackPayload
    from .user import User


__all__ = ("Track", "ListTrack")


class Track(Url):
    __slots__ = (
        "_state",
        "id",
        "uri",
        "external_urls",
        "name",
        "album",
        "artists",
        "markets",
        "disc_number",
        "duration",
        "explicit",
        "external_ids",
        "local",
        "popularity",
        "preview_url",
        "track_number",
    )

    if TYPE_CHECKING:
        id: SpotifyID
        uri: SpotifyURI
        external_urls: dict
        name: str
        album: Album
        artists: List[Artist]
        markets: List[str]
        local: bool
        popularity: int
        preview_url: str
        track_number: int

    def __init__(self, state, data: "TrackPayload") -> None:
        self._state: State = state
        self._update(data)

    def _update(self, data: "TrackPayload"):
        self.id = data["id"]
        self.uri = data["uri"]
        self.external_urls = data["external_urls"]
        self.name = data["name"]
        self.artists = [self._state.objectify(a) for a in data["artists"]]
        self.local = data["is_local"]
        self.preview_url = data["preview_url"]
        self.track_number = data["track_number"]

        if "album" in data:
            self.album = self._state.objectify(data["album"])
        else:
            self.album = None

        self.markets = data.get("available_markets")
        self.popularity = data.get("popularity")

    async def fetch(self) -> None:
        self._update(await self._state.http.get_track(self.id))

    def __repr__(self) -> str:
        attrs = " ".join(f"{name}={getattr(self, name)}" for name in ["id", "name"])
        return f"<{self.__class__.__qualname__} {attrs}>"


class ListTrack(Track):
    __slots__ = ("added_at",)

    def __init__(self, state, data: "ListTrackPayload") -> None:
        super().__init__(state, data["track"])

        self.added_at = fromspotifyiso(data["added_at"])

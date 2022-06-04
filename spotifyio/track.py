from typing import List

from .utils.time import fromspotifyiso

from .http import HTTPClient
from .artist import Artist
from .album import Album
from .mixins import Url


class Track(Url):
    __slots__ = (
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

    def __init__(self, http: HTTPClient, data: dict) -> None:
        self._http = http

        self.id: str = data["id"]
        self.uri: str = data["uri"]
        self.external_urls: dict = data["external_urls"]
        self.name: str = data["name"]
        self.album: Album = Album(self._http, data["album"])
        self.artists: List[Artist] = [Artist(self._http, a) for a in data["artists"]]
        self.markets: List[str] = data["available_markets"]
        self.local: bool = data["is_local"]
        self.popularity: int = data["popularity"]
        self.preview_url: str = data["preview_url"]
        self.track_number: int = data["track_number"]

    def __repr__(self) -> str:
        attrs = " ".join(f"{name}={getattr(self, name)}" for name in ["id", "name"])
        return f"<{self.__class__.__qualname__} {attrs}>"


class ListTrack(Track):
    __slots__ = ("added_at",)

    def __init__(self, http: HTTPClient, data: dict) -> None:
        super().__init__(http, data["track"])

        self.added_at = fromspotifyiso(data["added_at"])

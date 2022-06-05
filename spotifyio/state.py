from .http import HTTPClient

from .album import Album, ListAlbum
from .artist import Artist
from .track import Track


class State:
    __slots__ = ("http",)

    def __init__(self, http: HTTPClient) -> None:
        self.http = http

    def album(self, data: dict):
        return Album(self, data)

    def list_album(self, data: dict):
        return ListAlbum(self, data)

    def artist(self, data: dict):
        return Artist(self, data)

    def track(self, data: dict):
        return Track(self, data)

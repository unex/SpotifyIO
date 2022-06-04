from .http import HTTPClient

from .album import Album
from .artist import Artist
from .track import Track


class State:
    __slots__ = ("http",)

    def __init__(self, http: HTTPClient) -> None:
        self.http = http

    def album(self, data: dict):
        return Album(self, data)

    def artist(self, data: dict):
        return Artist(self, data)

    def track(self, data: dict):
        return Track(self, data)

from .http import HTTPClient

from .album import Album, ListAlbum
from .artist import Artist
from .track import Track, ListTrack
from .user import User

OBJ_MAPPING = {
    "user": User,
    "track": Track,
    "list_track": ListTrack,
    "album": Album,
    "list_album": ListAlbum,
    "artist": Artist,
}

class State:
    __slots__ = ("http",)

    def __init__(self, http: HTTPClient) -> None:
        self.http = http

    def objectify(self, data: dict):

        # is a listing
        if 'added_at' in data:
            _type = "list_" + list(data.keys())[1]
        else:
            _type = data["type"]

        try:
            return OBJ_MAPPING[_type](self, data)
        except KeyError:
            raise NotImplementedError(f"{_type} not supported in State.objectify")

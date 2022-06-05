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
        if "added_at" in data:
            for key in list(data.keys()):
                if key in OBJ_MAPPING:
                    _type = f"list_{key}"
                    break

        else:
            _type = data["type"]

        if _type not in OBJ_MAPPING:
            raise NotImplementedError(f"{_type} not supported in State.objectify")

        return OBJ_MAPPING[_type](self, data)

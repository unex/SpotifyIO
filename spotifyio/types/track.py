from typing import TYPE_CHECKING, List

from .payload import Payload
from .list_item import ListItemPayload

if TYPE_CHECKING:
    from .album import AlbumPayload
    from .artist import ArtistPayload
    from .user import UserPayload


class TrackPayload(Payload, total=False):
    album: "AlbumPayload"
    artists: List["ArtistPayload"]
    available_markets: dict
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: dict
    is_local: bool
    name: str
    popularity: int
    preview_url: str
    track_number: int


class ListTrackPayload(ListItemPayload):
    added_by: "UserPayload"
    is_local: bool
    track: TrackPayload

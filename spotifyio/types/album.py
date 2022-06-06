from typing import TYPE_CHECKING, List

from .asset import AssetPayload
from .list_item import ListItemPayload
from .payload import Payload

if TYPE_CHECKING:
    from .artist import ArtistPayload
    from .track import TrackPayload


class AlbumPayload(Payload, total=False):
    album_type: str
    artists: List["ArtistPayload"]
    available_markets: List[str]
    copyrights: dict
    external_ids: dict
    genres: List[str]
    images: List[AssetPayload]
    label: str
    name: str
    popularity: int
    release_date: str
    release_date_precision: str
    total_tracks: int
    tracks: List["TrackPayload"]


class ListAlbumPayload(ListItemPayload):
    album: "AlbumPayload"

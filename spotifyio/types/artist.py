from typing import List, TypedDict

from .payload import Payload
from .asset import AssetPayload


class ArtistPayload(Payload, total=False):
    followers: int
    genres: List[str]
    images: List[AssetPayload]
    name: str
    popularity: int

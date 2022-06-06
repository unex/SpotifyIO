from typing import List, TypedDict

from .asset import AssetPayload
from .payload import Payload


class ArtistPayload(Payload, total=False):
    followers: int
    genres: List[str]
    images: List[AssetPayload]
    name: str
    popularity: int

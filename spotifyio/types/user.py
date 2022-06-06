from typing import List

from .payload import Payload
from .asset import AssetPayload
from .spotify import SpotifyUserID


class UserPayload(Payload, total=False):
    display_name: str
    followers: dict
    id: SpotifyUserID
    images: List[AssetPayload]


class ClientUserPayload(UserPayload, total=False):
    country: str
    email: str
    explicit_content: dict
    product: str

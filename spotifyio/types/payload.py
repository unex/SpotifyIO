from typing import TypedDict

from .spotify import SpotifyID, SpotifyURI


class Payload(TypedDict, total=False):
    external_urls: dict
    type: str
    href: str
    id: SpotifyID
    uri: SpotifyURI

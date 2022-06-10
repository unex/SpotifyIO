from dataclasses import dataclass
from typing import Optional


@dataclass
class Asset:
    """A Spotify asset.

    Attributes:
        width (:class:`int`): asset width.
        height (:class:`int`): asset height.
        url (:class:`str`): asset url.
    """

    width: Optional[int]
    height: Optional[int]
    url: str

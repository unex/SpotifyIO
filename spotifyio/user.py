from typing import TYPE_CHECKING, List, Optional

from .http import HTTPClient
from .asset import Asset
from .mixins import Url

if TYPE_CHECKING:
    from .state import State
    from .artist import Artist
    from .track import Track, ListTrack

class User(Url):
    __slots__ = (
        "id",
        "uri",
        "external_urls",
        "display_name",
        "followers",
        "images",
        "email",
        "country",
        "product",
        "explicit_content",
    )

    def __init__(self, state, data: dict) -> None:
        self._state = state

        self.id: str = data["id"]
        self.uri: str = data["uri"]
        self.external_urls: dict = data["external_urls"]
        self.display_name: str = data["display_name"]
        self.followers: int = data["followers"]["total"]
        self.images: List[Asset] = [Asset(**a) for a in data["images"]]

        self.email: Optional[str] = data.get("email")  # user-read-email
        self.country: Optional[str] = data.get("country")  # user-read-private
        self.product: Optional[str] = data.get("product")  # user-read-private
        self.explicit_content: Optional[dict] = data.get(
            "explicit_content"
        )  # user-read-private


class ClientUser(User):
    __slots__ = ()


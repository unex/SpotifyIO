from typing import TYPE_CHECKING, Iterable, List, Optional

from .utils.chunked import Chunked
from .utils.paginator import Paginator
from .utils.list_iterator import ListIterator

from .asset import Asset
from .mixins import Url

if TYPE_CHECKING:
    from .state import State
    from .album import Album
    from .artist import Artist
    from .track import Track, ListTrack


class ClientUserAlbums(ListIterator["Album"]):
    def __init__(self, state, *args, **kwargs) -> None:
        self._state: State = state

        super().__init__(*args, **kwargs)

    async def save(self, *albums: Iterable["Album"]) -> None:
        for chunk in Chunked(albums, 20):
            await self._state.http.put_me_albums(list(map(lambda x: x.id, chunk)))

    async def remove(self, *albums: Iterable["Album"]) -> None:
        for chunk in Chunked(albums, 20):
            await self._state.http.delete_me_albums(list(map(lambda x: x.id, chunk)))

    async def contains(self, *albums: Iterable["Album"]) -> List[bool]:
        for chunk in Chunked(albums, 20):
            return await self._state.http.get_me_albums_contains(
                list(map(lambda x: x.id, chunk))
            )


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

    @property
    def albums(self, market: str = None) -> ClientUserAlbums["Album"]:
        async def gen():
            async for data in Paginator(self._state.http.get_me_albums):
                yield self._state.list_album(data)

        return ClientUserAlbums(self._state, gen())

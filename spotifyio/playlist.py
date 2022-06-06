from typing import TYPE_CHECKING, Iterable, List

from .asset import Asset
from .mixins import Followable, Url
from .types import SpotifyID, SpotifyURI
from .utils.chunked import Chunked
from .utils.list_iterator import ListIterator
from .utils.paginator import Paginator

if TYPE_CHECKING:
    from .state import State
    from .track import ListTrack, Track
    from .types import PlaylistPayload
    from .user import User

__all__ = ("Playlist",)


class Playlist(Url, Followable):
    __slots__ = (
        "_state",
        "_tracks",
        "id",
        "uri",
        "external_urls",
        "name",
        "description",
        "images",
        "owner",
        "primary_color",
        "public",
        "collaborative",
        "snapshot_id",
    )

    if TYPE_CHECKING:
        id: SpotifyID
        uri: SpotifyURI
        external_urls: dict
        name: str
        description: str
        images: List[Asset]
        owner: User
        primary_color: str
        public: bool
        collaborative: bool
        snapshot_id: str

    def __init__(self, state, data: "PlaylistPayload") -> None:
        self._state: State = state
        self._update(data)

    def _update(self, data: "PlaylistPayload"):
        self.id = data["id"]
        self.uri = data["uri"]
        self.external_urls = data["external_urls"]
        self.name = data["name"]
        self.description = data["description"]
        self.images = [Asset(**a) for a in data["images"]]
        self.owner = self._state.objectify(data["owner"])
        self.primary_color = data["primary_color"]
        self.public = data["public"]
        self.collaborative = data["collaborative"]
        self.snapshot_id = data["snapshot_id"]

        self._tracks = data["tracks"]

    async def edit(
        self,
        *,
        name: str = None,
        description: str = None,
        public: bool = None,
        collaborative: bool = None,
    ):
        await self._state.http.put_playlist(
            self.id,
            name=name,
            description=description,
            public=public,
            collaborative=collaborative,
        )

    @property
    def tracks(self) -> ListIterator["ListTrack"]:
        async def gen():
            async for data in Paginator(
                self._state.http.get_playlist_tracks, self.id, _data=self._tracks
            ):
                yield self._state.objectify(data)

        return ListIterator(gen())

    async def add(self, *tracks: Iterable["Track"], position: int = None) -> None:
        for chunk in Chunked(tracks, 100):
            self.snapshot_id = await self._state.http.post_playlist_tracks(
                self.id, uris=list(map(lambda x: x.uri, chunk)), position=position
            )

    async def update(self, *albums: Iterable["Track"]) -> None:
        for chunk in Chunked(albums, 20):
            await self._state.http.put_playlist_tracks(list(map(lambda x: x.id, chunk)))

    async def update_image(self, image: bytes) -> None:
        await self._state.http.put_playlist_image(self.id, image=image)

    async def remove(self, *albums: Iterable["Track"]) -> None:
        for chunk in Chunked(albums, 20):
            await self._state.http.delete_playlist_tracks(
                self.id,
                uris=list(map(lambda x: x.uri, chunk)),
                snapshot_id=self.snapshot_id,
            )

    async def contains(self, *albums: Iterable["Track"]) -> List[bool]:
        for chunk in Chunked(albums, 20):
            return await self._state.http.get_playlist_tracks_contains(
                list(map(lambda x: x.id, chunk))
            )

    def __repr__(self) -> str:
        attrs = " ".join(
            f"{name}={getattr(self, name)}" for name in ["id", "name", "snapshot_id"]
        )
        return f"<{self.__class__.__qualname__} {attrs}>"
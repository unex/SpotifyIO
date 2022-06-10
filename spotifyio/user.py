from typing import TYPE_CHECKING, Iterable, List, Optional

from .asset import Asset
from .mixins import Followable, Url
from .types import SpotifyURI, SpotifyUserID
from .utils.chunked import Chunked
from .utils.list_iterator import ListIterator
from .utils.paginator import Paginator

if TYPE_CHECKING:
    from .album import Album
    from .artist import Artist
    from .playlist import Playlist
    from .state import State
    from .track import ListTrack, Track
    from .types import ClientUserPayload, UserPayload


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


class User(Url, Followable):
    """A Spotify User.

    Attributes:
        id (:class:`str`): The user’s unique ID.
        uri (:class:`str`): The user’s Spotify URI.
        external_urls (:class:`dict`): External links to this user.
        display_name (:class:`str`): The user's name.
        followers (:class:`int`): The user's followers.
        images (List[:class:`.Asset`]): Profile image for this user.
    """

    __slots__ = (
        "_state",
        "_followers",
        "id",
        "uri",
        "external_urls",
        "display_name",
        "images",
    )

    if TYPE_CHECKING:
        id: SpotifyUserID
        uri: SpotifyURI
        external_urls: dict
        display_name: str
        images: List[Asset]

    def __init__(self, state, data: "UserPayload") -> None:
        self._state: State = state
        self._update(data)

    def _update(self, data: "UserPayload") -> None:
        self.id = data["id"]
        self.uri = data["uri"]

        self.external_urls = data.get("external_urls")
        self.display_name = data.get("display_name")
        self._followers = data.get("followers")

        if "images" in data:
            self.images = [Asset(**a) for a in data["images"]]
        else:
            self.images = None

    def playlists(self) -> ListIterator["Playlist"]:
        """An asynchronous iterator for the users's saved playlists.

        Yields:
            :class:`.Playlist`:
        """
        async def gen():
            async for data in Paginator(self._state.http.get_user_playlists, self.id):
                yield self._state.objectify(data)

        return ListIterator(gen())

    def __repr__(self) -> str:
        attrs = " ".join(
            f"{name}={getattr(self, name)}" for name in ["id", "display_name"]
        )
        return f"<{self.__class__.__qualname__} {attrs}>"


class ClientUser(User):
    """The currently authenticated Spotify User.

    Attributes:
        email (:class:`str`): The user’s email, requires `user-read-email` scope.
        country (:class:`str`): The user’s country, requires `user-read-private` scope.
        product (:class:`str`): If this account is premium, requires `user-read-private` scope.
        explicit_content (:class:`dict`): The user's explicit content settings, requires `user-read-private` scope.
    """

    __slots__ = (
        "email",
        "country",
        "product",
        "explicit_content",
    )

    if TYPE_CHECKING:
        email: Optional[str]
        country: Optional[str]
        product: Optional[str]
        explicit_content: Optional[dict]

    def _update(self, data: "ClientUserPayload") -> None:
        super()._update(data)

        self.email = data.get("email")  # user-read-email
        self.country = data.get("country")  # user-read-private
        self.product = data.get("product")  # user-read-private
        self.explicit_content = data.get("explicit_content")  # user-read-private

    def albums(self, market: str = None) -> ClientUserAlbums["Album"]:
        """An asynchronous iterator for the users's saved albums.

        Yields:
            :class:`.Album`:
        """
        async def gen():
            async for data in Paginator(self._state.http.get_me_albums):
                yield self._state.objectify(data)

        return ClientUserAlbums(self._state, gen())

    def playlists(self) -> ListIterator["Playlist"]:
        async def gen():
            async for data in Paginator(self._state.http.get_me_playlists):
                yield self._state.objectify(data)

        return ListIterator(gen())

    async def create_playlist(
        self,
        name: str,
        description: str = None,
        public: bool = True,
        collaborative: bool = False,
    ) -> "Playlist":
        """Creates a new playlist.

        Parameters:
            name (:class:`str`)
            description (:class:`str`)
            public (:class:`bool`)
            collaborative (:class:`bool`)

        Returns:
            :class:`.Playlist`
        """
        return self._state.objectify(
            await self._state.http.post_user_playlists(
                self.id,
                name=name,
                description=description,
                public=public,
                collaborative=collaborative,
            )
        )


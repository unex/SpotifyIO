import asyncio
from types import TracebackType
from typing import Any, List, Optional, Type

from .album import Album
from .artist import Artist
from .auth import FLOWS, Token
from .http import HTTPClient
from .iterators import GenericAsyncIterator
from .playlist import Playlist
from .state import State
from .track import Track
from .types import SpotifyID, SpotifyUserID
from .user import ClientUser, User
from .utils.chunked import Chunked
from .utils.paginator import Paginator


class Client:
    """SpotifyIO Client object that is used to interact with the Spotify API.

    Attributes:
        token (Optional[:class:`.Token`]): The current auth token. Could be ``None``.
    """

    def __init__(self, auth_flow: FLOWS, **options: Any) -> None:
        self._loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

        self._http = HTTPClient(
            self._loop,
            auth_flow,
        )

        self._state = State(self._http)

    async def __aenter__(self):
        await self.prepare()
        return self

    async def prepare(self) -> None:
        await self._http.prepare()

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.close()

    async def close(self) -> None:
        await self._http.close()

    @property
    def token(self) -> Token:
        return self._http.auth.token

    async def me(self) -> ClientUser:
        """:class:`.ClientUser`: Retrieves the currently authenticated user"""
        return ClientUser(self._state, await self._http.get_me())

    async def fetch_album(self, album_id: SpotifyID) -> Album:
        """Retrieve an album with the given ID.

        Args:
            album_id (:class:`str`): The album's ID to fetch

        Raises:
            HTTPException: Retrieving the album failed.

        Returns:
            :class:`.Album`: The album from the ID.
        """
        return self._state.objectify(await self._http.get_album(album_id))

    def fetch_albums(self, *album_ids: List[SpotifyID]) -> GenericAsyncIterator[Album]:
        """An asynchronous iterator for multiple Albums.

        Args:
            \*album_ids (:class:`str`): Argument list of album ids

        Raises:
            HTTPException: Retrieving the album failed.

        Yields:
            :class:`.Album`: An Album.
        """

        async def gen():
            for chunk in Chunked(album_ids, 50):
                for album in await self._http.get_albums(chunk):
                    yield self._state.objectify(album)

        return GenericAsyncIterator(gen())

    async def fetch_artist(self, artist_id: SpotifyID) -> Artist:
        """Retrieve an artist with the given ID.

        Args:
            artist_id (:class:`str`): The artist's ID to fetch

        Raises:
            HTTPException: Retrieving the album failed.

        Returns:
            :class:`.Artist`: The artist from the ID.
        """
        return self._state.objectify(await self._http.get_artist(artist_id))

    def fetch_artists(self, *artist_ids: List[SpotifyID]) -> GenericAsyncIterator[Artist]:
        """An asynchronous iterator for multiple Artists.

        Args:
            \*artist_ids (:class:`str`): Argument list of artist ids

        Raises:
            HTTPException: Retrieving the artist failed.

        Yields:
            :class:`.Artist`: An Artist.
        """

        async def gen():
            for chunk in Chunked(artist_ids, 50):
                for artist in await self._http.get_artists(chunk):
                    yield self._state.objectify(artist)

        return GenericAsyncIterator(gen())

    async def fetch_track(self, track_id: SpotifyID) -> Track:
        """Retrieve a track with the given ID.

        Args:
            track_id (:class:`str`): The track's ID to fetch

        Raises:
            HTTPException: Retrieving the track failed.

        Returns:
            :class:`.Track`: The track from the ID.
        """
        return self._state.objectify(await self._http.get_track(track_id))

    def fetch_tracks(self, *track_ids: List[SpotifyID]) -> GenericAsyncIterator[Track]:
        """An asynchronous iterator for multiple Tracks.

        .. :async-for:

        Args:
            \*track_ids (:class:`str`): Argument list of track ids

        Raises:
            HTTPException: Retrieving the track failed.

        Yields:
            :class:`.Track`: A Track.
        """

        async def gen():
            for chunk in Chunked(track_ids, 50):
                for track in await self._http.get_tracks(chunk):
                    yield self._state.objectify(track)

        return GenericAsyncIterator(gen())

    async def fetch_user(self, user_id: SpotifyUserID) -> User:
        """Retrieve a user with the given ID.

        Args:
            user_id (:class:`str`): The user's ID to fetch

        Raises:
            HTTPException: Retrieving the user failed.

        Returns:
            :class:`.User`: The user from the ID.
        """
        return self._state.objectify(await self._http.get_user(user_id))

    async def fetch_playlist(self, playlist_id: SpotifyID) -> Playlist:
        """Retrieve a playlist with the given ID.

        Args:
            playlist_id (:class:`str`): The playlist's ID to fetch

        Raises:
            HTTPException: Retrieving the playlist failed.

        Returns:
            :class:`.Playlist`: The playlist from the ID.
        """
        return self._state.objectify(await self._http.get_playlist(playlist_id))

    def new_album_releases(self, country: str = None) -> GenericAsyncIterator[Album]:
        """An asynchronous iterator for new Album releases.

        Yields:
            :class:`.Album`: An Album.
        """

        async def gen():
            async for data in Paginator(self._http.get_browse_new_releases, country_code=country):
                yield self._state.objectify(data)

        return GenericAsyncIterator(gen())

    def featured_playlists(self, country: str = None) -> GenericAsyncIterator[Playlist]:
        """An asynchronous iterator for featured Playlists.

        Yields:
            :class:`.Playlist`: A Playlist.
        """

        async def gen():
            async for data in Paginator(self._http.get_browse_featured_playlists, country_code=country):
                yield self._state.objectify(data)

        return GenericAsyncIterator(gen())

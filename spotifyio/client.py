import asyncio

from typing import List, Optional, Type, Any
from types import TracebackType

from .utils.chunked import Chunked
from .utils.list_iterator import ListIterator

from .auth import FLOWS, Token
from .http import HTTPClient
from .state import State

from .album import Album
from .artist import Artist
from .track import Track
from .user import ClientUser


class Client:
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
        return ClientUser(self._http, await self._http.fetch_me())

    async def fetch_album(self, album_id: str) -> Album:
        return self._state.album(await self._http.get_album(album_id))

    def fetch_albums(self, *album_ids: List[str]) -> ListIterator[Album]:
        async def gen():
            for chunk in Chunked(album_ids, 50):
                for album in await self._http.get_albums(chunk):
                    yield self._state.album(album)

        return ListIterator(gen())

    async def fetch_artist(self, artist_id: str) -> Artist:
        return self._state.artist(await self._http.get_artist(artist_id))

    def fetch_artists(self, *artist_ids: List[str]) -> ListIterator[Artist]:
        async def gen():
            for chunk in Chunked(artist_ids, 50):
                for artist in await self._http.get_artists(chunk):
                    yield self._state.artist(artist)

        return ListIterator(gen())

    async def fetch_track(self, track_id: str) -> Track:
        return self._state.track(await self._http.get_track(track_id))

    def fetch_tracks(self, *track_ids: List[str]) -> ListIterator[Track]:
        async def gen():
            for chunk in Chunked(track_ids, 50):
                for track in await self._http.get_tracks(chunk):
                    yield self._state.track(track)

        return ListIterator(gen())

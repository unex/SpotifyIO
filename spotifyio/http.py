import sys
import asyncio

from typing import List, Optional, Any, Dict, ClassVar

import aiohttp
import orjson

from . import __version__
from .auth import FLOWS
from .exceptions import HTTPException, Forbidden, NotFound, ServerError


class Route:
    BASE: ClassVar[str] = "https://api.spotify.com/v1"

    def __init__(self, method: str, path: str, **parameters: Dict[str, Any]) -> None:
        self.method = method
        self.path = path
        self.url = self.BASE + self.path

        self.query = parameters


class HTTPClient:
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        auth: FLOWS,
        connector: Optional[aiohttp.BaseConnector] = None,
    ) -> None:
        self.loop = loop
        self.auth = auth
        self.connector = connector or None

        self.__session: aiohttp.ClientSession = None

        self.user_agent = f"SpotifyIO (https://github.com/unex/SpotifyIO {__version__}) Python/{sys.version_info} aiohttp/{aiohttp.__version__}"

    async def request(
        self,
        route: Route,
        **kwargs: Any,
    ) -> Any:
        method = route.method
        url = route.url

        token = await self.auth._get_access_token()

        headers: Dict[str, str] = {
            "User-Agent": self.user_agent,
            "Authorization": f"Bearer {token}",
        }

        kwargs["headers"] = headers

        for tries in range(5):
            try:
                async with self.__session.request(
                    method, url, params=route.query, **kwargs
                ) as response:
                    if text := await response.text():
                        data = orjson.loads(text)
                    else:
                        data = None

                    # TODO: ratelimiting

                    # Success
                    if 300 > response.status >= 200:
                        return data

                    if response.status in {500, 502, 504, 524}:
                        await asyncio.sleep(1 + tries * 2)
                        continue

                    # the usual error cases
                    if response.status == 403:
                        raise Forbidden(response, data)
                    elif response.status == 404:
                        raise NotFound(response, data)
                    elif response.status >= 500:
                        raise ServerError(response, data)
                    else:
                        raise HTTPException(response, data)

            except OSError as e:
                # Connection reset by peer
                if tries < 4 and e.errno in (54, 10054):
                    await asyncio.sleep(1 + tries * 2)
                    continue
                raise

    async def prepare(self):
        if self.connector is None:
            self.connector = aiohttp.TCPConnector(limit=None)

        self.__session = aiohttp.ClientSession(
            connector=self.connector,
            json_serialize=orjson.dumps,
        )

    async def close(self):
        await self.__session.close()

    async def fetch_me(self):
        route = Route("GET", "/me")
        return await self.request(route)

    # Albums

    async def get_album(self, album_id: str):
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-an-album"""
        route = Route("GET", f"/albums/{album_id}")
        return await self.request(route)

    async def get_albums(self, album_ids: List[str]):
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-multiple-albums"""
        route = Route("GET", "/albums", ids=",".join(album_ids))
        data = await self.request(route)
        return data["albums"]

    async def get_album_tracks(self, album_id: str, **kwargs):
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-an-albums-tracks"""
        route = Route("GET", f"/albums/{album_id}/tracks", **kwargs)
        return await self.request(route)

    async def get_me_albums(self, **kwargs):
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-users-saved-albums"""
        route = Route("GET", "/me/albums", **kwargs)
        return await self.request(route)

    async def put_me_albums(self, album_ids=List[str]):
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/save-albums-user"""
        route = Route("PUT", "/me/albums", ids=",".join(album_ids))
        await self.request(route)

    async def delete_me_albums(self, album_ids=List[str]):
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/remove-albums-user"""
        route = Route("DELETE", "/me/albums", ids=",".join(album_ids))
        await self.request(route)

    async def get_me_albums_contains(self, album_ids: List[str]):
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/check-users-saved-albums"""
        route = Route("GET", "/me/albums/contains", ids=",".join(album_ids))
        return await self.request(route)

    # Artists

    async def get_artist(self, artist_id: str):
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-an-artist"""
        route = Route("GET", f"/artists/{artist_id}")
        return await self.request(route)

    async def get_artists(self, artist_ids: List[str]):
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-multiple-artists"""
        route = Route("GET", "/artists", ids=",".join(artist_ids))
        data = await self.request(route)
        return data["artists"]

    # Tracks

    async def get_track(self, track_id: str):
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-track"""
        route = Route("GET", f"/tracks/{track_id}")
        return await self.request(route)

    async def get_tracks(self, track_ids: List[str]):
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-tracks"""
        route = Route("GET", "/tracks", ids=",".join(track_ids))
        data = await self.request(route)
        return data["tracks"]

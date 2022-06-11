import asyncio
import sys
from base64 import b64encode
from typing import Any, ClassVar, Dict, List, Optional

import aiohttp
import orjson

from . import __version__
from .auth import FLOWS
from .exceptions import Forbidden, HTTPException, NotFound, ServerError
from .types import (
    AlbumPayload,
    ArtistPayload,
    ClientUserPayload,
    ListAlbumPayload,
    ListTrackPayload,
    PaginatedPayload,
    PlaylistPayload,
    SnapshotID,
    SpotifyCategoryID,
    SpotifyID,
    SpotifyURI,
    SpotifyURL,
    SpotifyUserID,
    TrackPayload,
    UserPayload,
)


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
                async with self.__session.request(method, url, params=route.query, **kwargs) as response:
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
        )

    async def close(self):
        await self.__session.close()

    async def fetch_me(self) -> ClientUserPayload:
        route = Route("GET", "/me")
        return await self.request(route)

    # Albums

    async def get_album(self, album_id: SpotifyID) -> AlbumPayload:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-an-album"""
        route = Route("GET", f"/albums/{album_id}")
        return await self.request(route)

    async def get_albums(self, album_ids: List[SpotifyID]) -> List[AlbumPayload]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-multiple-albums"""
        route = Route("GET", "/albums", ids=",".join(album_ids))
        data = await self.request(route)
        return data["albums"]

    async def get_album_tracks(self, album_id: SpotifyID, **kwargs) -> PaginatedPayload[TrackPayload]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-an-albums-tracks"""
        route = Route("GET", f"/albums/{album_id}/tracks", **kwargs)
        return await self.request(route)

    async def get_me_albums(self, **kwargs) -> PaginatedPayload[ListAlbumPayload]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-users-saved-albums"""
        route = Route("GET", "/me/albums", **kwargs)
        return await self.request(route)

    async def put_me_albums(self, album_ids=List[SpotifyID]) -> None:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/save-albums-user"""
        route = Route("PUT", "/me/albums", ids=",".join(album_ids))
        await self.request(route)

    async def delete_me_albums(self, album_ids=List[SpotifyID]) -> None:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/remove-albums-user"""
        route = Route("DELETE", "/me/albums", ids=",".join(album_ids))
        await self.request(route)

    async def get_me_albums_contains(self, album_ids: List[SpotifyID]) -> List[bool]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/check-users-saved-albums"""
        route = Route("GET", "/me/albums/contains", ids=",".join(album_ids))
        return await self.request(route)

    async def get_browse_new_releases(self, country_code: str, **kwargs) -> PaginatedPayload[AlbumPayload]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-new-releases"""
        if country_code:
            kwargs["country"] = country_code

        route = Route("GET", "/browse/new-releases", **kwargs)
        data = await self.request(route)
        return data["albums"]

    # Artists

    async def get_artist(self, artist_id: SpotifyID) -> ArtistPayload:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-an-artist"""
        route = Route("GET", f"/artists/{artist_id}")
        return await self.request(route)

    async def get_artists(self, artist_ids: List[SpotifyID]) -> List[ArtistPayload]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-multiple-artists"""
        route = Route("GET", "/artists", ids=",".join(artist_ids))
        data = await self.request(route)
        return data["artists"]

    async def get_artist_albums(
        self, artist_id: SpotifyID, include: List[str] = [], **kwargs
    ) -> PaginatedPayload[AlbumPayload]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-an-artists-albums"""
        route = Route("GET", f"/artists/{artist_id}/albums", include_groups=include, **kwargs)
        return await self.request(route)

    async def get_artist_top_tracks(self, artist_id: SpotifyID, *, country_code: str) -> List[TrackPayload]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-an-artists-top-tracks"""
        route = Route("GET", f"/artists/{artist_id}/top-tracks", country=country_code)
        data = await self.request(route)
        return data["tracks"]

    async def get_artist_related(self, artist_id: SpotifyID) -> List[ArtistPayload]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-an-artists-related-artists"""
        route = Route("GET", f"/artists/{artist_id}/related-artists")
        data = await self.request(route)
        return data["artists"]

    # Tracks

    async def get_track(self, track_id: SpotifyID) -> TrackPayload:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-track"""
        route = Route("GET", f"/tracks/{track_id}")
        return await self.request(route)

    async def get_tracks(self, track_ids: List[SpotifyID]) -> List[TrackPayload]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-tracks"""
        route = Route("GET", "/tracks", ids=",".join(track_ids))
        data = await self.request(route)
        return data["tracks"]

    # Playlists

    async def get_playlist(self, playlist_id: SpotifyID) -> PlaylistPayload:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-playlist"""
        route = Route("GET", f"/playlists/{playlist_id}")
        return await self.request(route)

    async def put_playlist(
        self,
        playlist_id: SpotifyID,
        *,
        name: str,
        description: str,
        public: bool,
        collaborative: bool,
    ) -> None:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/change-playlist-details"""
        data = {}

        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if public:
            data["public"] = public
        if collaborative:
            data["collaborative"] = collaborative

        route = Route("PUT", f"/playlists/{playlist_id}")
        await self.request(route, json=data)

    async def get_playlist_tracks(self, playlist_id: SpotifyID, **kwargs) -> PaginatedPayload[TrackPayload]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-playlists-tracks"""
        route = Route("GET", f"/playlists/{playlist_id}/tracks", **kwargs)
        return await self.request(route)

    async def post_playlist_tracks(self, playlist_id: SpotifyID, *, uris: List[SpotifyURI], position: int) -> SnapshotID:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/add-tracks-to-playlist"""
        query = {
            "uris": ",".join(uris),
        }

        if position is not None:
            query["position"] = position

        route = Route("POST", f"/playlists/{playlist_id}/tracks", **query)
        data = await self.request(route)
        return data["snapshot_id"]

    async def put_playlist_tracks(
        self,
        playlist_id: SpotifyID,
        *,
        uris: List[SpotifyURI],
        range_start: int,
        insert_before: int,
        range_length: int,
        snapshot_id: SnapshotID,
    ):
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/reorder-or-replace-playlists-tracks"""
        raise NotImplementedError()

    async def delete_playlist_tracks(
        self, playlist_id: SpotifyID, *, uris: List[SpotifyURI], snapshot_id: SnapshotID
    ) -> SnapshotID:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/remove-tracks-playlist"""
        route = Route("DELETE", f"/playlists/{playlist_id}/tracks")
        data = await self.request(
            route,
            json={
                "tracks": list(map(lambda x: {"uri": x}, uris)),
                "snapshot_id": snapshot_id,
            },
        )
        return data["snapshot_id"]

    async def get_me_playlists(self, **kwargs) -> PaginatedPayload[PlaylistPayload]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-a-list-of-current-users-playlists"""
        route = Route("GET", "/me/playlists", **kwargs)
        return await self.request(route)

    async def get_user_playlists(self, user_id: SpotifyUserID, **kwargs) -> PaginatedPayload[PlaylistPayload]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-list-users-playlists"""
        route = Route("GET", f"/users/{user_id}/playlists", **kwargs)
        return await self.request(route)

    async def post_user_playlists(
        self,
        user_id: SpotifyUserID,
        *,
        name: str,
        description: str,
        public: bool,
        collaborative: bool,
    ) -> PlaylistPayload:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/create-playlist"""
        data = {
            "name": name,
            "public": public,
            "collaborative": collaborative,
        }

        if description:
            data["description"] = description

        route = Route("POST", f"/users/{user_id}/playlists")
        return await self.request(route, json=data)

    async def get_browse_featured_playlists(self, *, country_code: str, **kwargs) -> PaginatedPayload[PlaylistPayload]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-featured-playlists"""
        if country_code:
            kwargs["country"] = country_code

        route = Route("GET", "/browse/featured-playlists", **kwargs)
        data = await self.request(route)
        return data["playlists"]

    async def get_browse_category_playlists(
        self, category: str, *, country_code: str, **kwargs
    ) -> PaginatedPayload[PlaylistPayload]:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/get-a-categories-playlists"""
        if country_code:
            kwargs["country"] = country_code

        route = Route("GET", f"/browse/categories/{category}/playlists", **kwargs)
        data = await self.request(route)
        return data["playlists"]

    async def put_playlist_image(self, playlist_id: SpotifyID, *, image: bytes) -> None:
        """https://developer.spotify.com/documentation/web-api/reference/#/operations/upload-custom-playlist-cover"""
        route = Route("PUT", f"/playlists/{playlist_id}/images")
        await self.request(route, data=b64encode(image))

from datetime import datetime
from typing import TYPE_CHECKING, List

from .mixins import Url
from .types import SpotifyID, SpotifyURI
from .utils.time import fromspotifyiso

if TYPE_CHECKING:
    from .album import Album
    from .artist import Artist
    from .state import State
    from .types import ListTrackPayload, TrackPayload
    from .user import User


__all__ = ("Track", "ListTrack")


class Track(Url):
    """A Spotify Track.

    Attributes:
        id (:class:`str`): The track’s unique ID.
        uri (:class:`str`): The track’s Spotify URI.
        external_urls (:class:`dict`): External links to this track.
        name (:class:`str`): The track's name.
        album (:class:`.Album`): The album this track is part of.
        artists (List[:class:`Artist`]): The artists that created this track.
        markets (List[:class:`str`]): List of countries this track is avaliable in.
        disc_number (:class:`int`): The disc this track is on.
        duration (:class:`int`): The length of this track.
        explicit (:class:`bool`): If this track is explicit.
        local (:class:`bool`): If this track is local.
        popularity (:class:`bool`): Track popularity calculated by Spotify.
        preview_url: (:class:`str`): Link to an audio preview of this track.
        track_number (:class:`int`): The track number.
    """

    __slots__ = (
        "_state",
        "id",
        "uri",
        "external_urls",
        "name",
        "album",
        "artists",
        "markets",
        "disc_number",
        "duration",
        "explicit",
        "external_ids",
        "local",
        "popularity",
        "preview_url",
        "track_number",
    )

    if TYPE_CHECKING:
        id: SpotifyID
        uri: SpotifyURI
        external_urls: dict
        name: str
        album: Album
        artists: List[Artist]
        markets: List[str]
        local: bool
        popularity: int
        preview_url: str
        track_number: int

    def __init__(self, state, data: "TrackPayload") -> None:
        self._state: State = state
        self._update(data)

    def _update(self, data: "TrackPayload"):
        self.id = data["id"]
        self.uri = data["uri"]
        self.external_urls = data["external_urls"]
        self.name = data["name"]
        self.artists = [self._state.objectify(a) for a in data["artists"]]
        self.local = data["is_local"]
        self.preview_url = data["preview_url"]
        self.track_number = data["track_number"]

        if "album" in data:
            self.album = self._state.objectify(data["album"])
        else:
            self.album = None

        self.markets = data.get("available_markets")
        self.popularity = data.get("popularity")

    async def fetch(self) -> None:
        """Updates a partial of this object with all data"""
        self._update(await self._state.http.get_track(self.id))

    def __repr__(self) -> str:
        attrs = " ".join(f"{name}={getattr(self, name)}" for name in ["id", "name"])
        return f"<{self.__class__.__qualname__} {attrs}>"


class ListTrack(Track):
    """A special :class:`.Track`, usually found in playlists and :meth:`.ClientUser.tracks`

    Attributes:
        added_at (:class:`datetime`): When the track was added.
        added_by (:class:`.User`): Who the track was added by.
    """

    __slots__ = (
        "added_at",
        "added_by",
    )

    if TYPE_CHECKING:
        added_at: datetime
        added_by: User

    def __init__(self, state, data: "ListTrackPayload") -> None:
        super().__init__(state, data["track"])

        self.added_at = fromspotifyiso(data["added_at"])

        if "added_by" in data:
            self.added_by = self._state.objectify(data["added_by"])
        else:
            self.added_by = None

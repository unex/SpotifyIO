from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from typing import Iterable
from urllib.parse import parse_qsl, urlencode, urlparse

from aiohttp import BasicAuth, ClientSession

from .scopes import Scopes


class Token:
    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        expires_in: int,
        **kwargs,
    ) -> None:
        self.access_token = access_token
        self.refresh_token = refresh_token

        self.expires_at: datetime = datetime.now(tz=timezone.utc) + timedelta(
            seconds=expires_in
        )

    @classmethod
    def from_refresh(cls, token):
        return cls(
            access_token=None,
            refresh_token=token,
            expires_in=0,
        )

    @property
    def expired(self):
        return self.access_token is None or self.expires_at <= datetime.now(
            tz=timezone.utc
        )


class AuthorizationFlow:
    client_id: str
    client_secret: str
    token: Token = None

    async def _get_access_token(self):
        if not self.token or self.token.expired:
            await self._update_token()

        return self.token.access_token

    async def _api_token(self, **kwargs) -> dict:
        async with ClientSession(raise_for_status=True) as session:
            async with session.post(
                "https://accounts.spotify.com/api/token",
                auth=BasicAuth(self.client_id, self.client_secret),
                **kwargs,
            ) as r:
                return await r.json()

    async def _token_refresh(self) -> None:
        data = await self._api_token(
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.token.refresh_token,
            }
        )

        self.token = Token(**data, refresh_token=self.token.refresh_token)

    async def _update_token(self) -> None:
        raise NotImplementedError()


class AuthorizationCodeFlow(AuthorizationFlow):
    redirect_uri: str
    scopes: Scopes | Iterable[str]

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: Scopes | Iterable[str],
        token: Token = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.token = token

    @property
    def url(self) -> str:
        self.state = token_urlsafe(32)

        return "https://accounts.spotify.com/authorize?" + urlencode(
            {
                "response_type": "code",
                "client_id": self.client_id,
                "scope": ",".join(self.scopes),
                "redirect_uri": self.redirect_uri,
                "state": self.state,
            }
        )

    async def user_authorization(self):
        print(self.url)
        url = input("Callback: ")

        await self.verify_url(url)

    async def verify_url(self, url: str, verify_state=True) -> None:
        query = dict(parse_qsl(urlparse(url).query))

        if verify_state and query.get("state") != self.state:
            raise

        self.state = None

        code = query.get("code")

        data = await self._api_token(
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
            }
        )

        self.token = Token(**data)

    async def _update_token(self) -> None:
        if not self.token:
            await self.user_authorization()

        if self.token.refresh_token:
            await self._token_refresh()


FLOWS = AuthorizationCodeFlow

import asyncio

from typing import TYPE_CHECKING, Optional, Type, Any
from types import TracebackType

from .auth import FLOWS, Token
from .http import HTTPClient
from .user import ClientUser


class Client:
    def __init__(self, auth_flow: FLOWS, **options: Any) -> None:
        self._loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

        self._http = HTTPClient(
            self._loop,
            auth_flow,
        )

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

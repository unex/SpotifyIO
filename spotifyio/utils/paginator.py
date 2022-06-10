from typing import Callable, Awaitable

from ..types import PaginatedPayload


class Paginator:
    API_LIMIT = 50  # fingers crossed this is constant....

    def __init__(
        self, func: Callable[..., Awaitable[PaginatedPayload]], *args, **kwargs
    ) -> None:
        self._func = func

        self._limit: int = kwargs.pop("limit", None)
        self._total: int = float("inf")

        self.count: int = 0
        self.data: list = []

        if _data := kwargs.get("_data"):
            self.data = _data["items"]
            self._total = _data["total"]

        self._args = args
        self._kwargs = kwargs

    def __aiter__(self):
        return self

    async def _make_req(self):
        kwargs = self._kwargs

        if not self._limit is None:
            remaining = self._limit - self.count

        if self._limit is None or remaining > self.API_LIMIT:
            limit = 50
        else:
            limit = remaining

        kwargs["limit"] = limit
        kwargs["offset"] = self.count

        req = await self._func(*self._args, **kwargs)

        self._total = req.pop("total")

        self.data = req.pop("items")

    async def __anext__(self):
        if self._limit is not None and self.count == self._limit:
            raise StopAsyncIteration

        if self._total == self.count:
            raise StopAsyncIteration

        if not self.data:
            await self._make_req()

        # this should never happen
        if not self.data:
            raise StopAsyncIteration

        self.count += 1

        return self.data.pop(0)

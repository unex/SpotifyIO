from typing import AsyncIterator, List, Optional, TypeVar

T = TypeVar("T")


class GenericAsyncIterator(AsyncIterator[T]):
    __slots__ = ("iterator",)

    def __init__(self, iterator) -> None:
        self.iterator = iterator

    def __aiter__(self) -> AsyncIterator[T]:
        return self.iterator

    async def __anext__(self) -> T:
        return await self.iterator.next()

    async def flatten(self, *, limit: Optional[int] = None) -> List[T]:
        ret = []

        async for item in self:
            if limit is not None and len(ret) >= limit:
                break

            ret.append(item)

        return ret

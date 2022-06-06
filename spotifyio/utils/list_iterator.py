from typing import AsyncGenerator, AsyncIterable, AsyncIterator, List, TypeVar

T = TypeVar("T")


class ListIterator(AsyncIterable[T]):
    def __init__(self, generator: AsyncGenerator) -> None:
        self._generator = generator

    def __aiter__(self) -> AsyncIterator[T]:
        return self._generator

    async def to_list(self, limit: int = None) -> List[T]:
        ret = []

        async for item in self:
            if limit is not None and len(ret) >= limit:
                break

            ret.append(item)

        return ret

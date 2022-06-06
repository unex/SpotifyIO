from typing import Generic, Iterable, Iterator, TypeVar

T = TypeVar("T")


class Chunked(Generic[T]):
    def __init__(self, iter_: Iterable[T], chunk_size: int) -> None:
        self.data = iter_
        self.chunk_size = chunk_size

    def __iter__(self) -> Iterator[T]:
        self.range = iter(range(0, len(self.data), self.chunk_size))
        return self

    def __next__(self):
        i = next(self.range)
        return self.data[i : i + self.chunk_size]

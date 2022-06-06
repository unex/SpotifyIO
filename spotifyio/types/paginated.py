from typing import TYPE_CHECKING, Any, Optional, List, TypedDict, TypeVar

T = TypeVar("T")

# TypedDict[T] will not be supported until 3.11, see https://github.com/python/cpython/issues/89026
class PaginatedPayload(TypedDict[T] if TYPE_CHECKING else TypedDict):
    items: List[T]
    limit: int
    next: Optional[str]
    previous: Optional[str]
    offset: int
    total: int

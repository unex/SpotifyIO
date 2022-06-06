from typing import Optional, TypedDict


class AssetPayload(TypedDict):
    url: str
    width: Optional[int]
    height: Optional[int]

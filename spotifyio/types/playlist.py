from typing import List, NewType

from .asset import AssetPayload
from .payload import Payload

SnapshotID = NewType("SnapshotID", str)


class PlaylistPayload(Payload):
    name: str
    description: str
    images: List["AssetPayload"]
    owner: dict
    primary_color: str
    public: bool
    collaborative: bool
    snapshot_id: SnapshotID

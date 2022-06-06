from typing import List, NewType

from .payload import Payload
from .asset import AssetPayload


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

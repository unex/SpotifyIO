from dataclasses import dataclass
from typing import Optional


@dataclass
class Asset:
    width: Optional[int]
    height: Optional[int]
    url: str

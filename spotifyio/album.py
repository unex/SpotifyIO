from typing import TYPE_CHECKING, List, Literal

from .mixins import Url

if TYPE_CHECKING:
    from .state import State
    from .track import Track

class Album(Url):
    def __init__(self, state, data: dict) -> None:
        self._state: State = state


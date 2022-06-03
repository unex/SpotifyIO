from .http import HTTPClient
from .mixins import Url


class Album(Url):
    def __init__(self, http: HTTPClient, data: dict) -> None:
        self._http = http

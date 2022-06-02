from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from aiohttp import ClientResponse


class SpotifyException(Exception):
    pass


class ClientException(SpotifyException):
    pass


class HTTPException(SpotifyException):
    def __init__(self, response: "ClientResponse", data: Optional[Dict[str, Any]]):
        self.response = response
        self.status: int = response.status
        self.code: int = 0
        self.text: str = ""

        if isinstance(data, dict) and "error" in data:
            error = data.get("error")
            self.code = error.get("status")
            self.text = error.get("message")

        super().__init__(
            f"{self.code} {self.text} ({self.status} {self.response.reason})"
        )


class Forbidden(HTTPException):
    pass


class NotFound(HTTPException):
    pass


class ServerError(HTTPException):
    pass

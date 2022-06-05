class Url:
    @property
    def url(self) -> str:
        return self.external_urls["spotify"]


class Followable:
    @property
    def followers(self) -> int:
        if self._followers:
            return self._followers["total"]
        return None

class Url:
    @property
    def url(self) -> str:
        return self.external_urls["spotify"]

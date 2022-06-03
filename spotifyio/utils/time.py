from datetime import datetime, timezone


def fromspotifyiso(date_string: str) -> datetime:
    return datetime.fromisoformat(date_string[:-1]).replace(tzinfo=timezone.utc)

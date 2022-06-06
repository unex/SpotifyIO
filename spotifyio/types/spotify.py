from typing import NewType

# https://developer.spotify.com/documentation/web-api/#spotify-uris-and-ids

SpotifyURI = NewType("SpotifyURI", str)
SpotifyID = NewType("SpotifyID", str)
SpotifyCategoryID = NewType("SpotifyCategoryID", SpotifyID)
SpotifyUserID = NewType("SpotifyUserID", SpotifyID)
SpotifyURL = NewType("SpotifyURL", str)

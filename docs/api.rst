.. currentmodule:: spotifyio

API Reference
===============

Client
~~~~~~~

.. attributetable:: Client
.. autoclass:: Client
    :members:
    :exclude-members: fetch_albums, fetch_artists, fetch_tracks, new_album_releases, featured_playlists

    .. autocomethod:: fetch_albums
        :async-for:

    .. autocomethod:: fetch_artists
        :async-for:

    .. autocomethod:: fetch_tracks
        :async-for:

    .. autocomethod:: new_album_releases
        :async-for:

    .. autocomethod:: featured_playlists
        :async-for:

Album
~~~~~~~

.. attributetable:: Album
.. autoclass:: Album()
    :members:
    :exclude-members: tracks

    .. autocomethod:: tracks
        :async-for:

Artist
~~~~~~~

.. attributetable:: Artist
.. autoclass:: Artist()
    :members:
    :exclude-members: albums, related, top_tracks

    .. autocomethod:: albums
        :async-for:

    .. autocomethod:: related
        :async-for:

    .. autocomethod:: top_tracks
        :async-for:

Playlist
~~~~~~~~

.. attributetable:: Playlist
.. autoclass:: Playlist()
    :members:
    :exclude-members: tracks

    .. autocomethod:: tracks
        :async-for:

Track
~~~~~~~

.. attributetable:: Track
.. autoclass:: Track()
    :members:

ListTrack
~~~~~~~~~

.. attributetable:: ListTrack
.. autoclass:: ListTrack()
    :members:

User
~~~~~~~

.. attributetable:: User
.. autoclass:: User()
    :members:
    :exclude-members: playlists

    .. autocomethod:: playlists
        :async-for:

ClientUser
~~~~~~~~~~

.. attributetable:: ClientUser
.. autoclass:: ClientUser()
    :members:
    :exclude-members: albums, playlists, top

    .. autocomethod:: albums
        :async-for:

    .. autocomethod:: playlists
        :async-for:

    .. autocomethod:: top
        :async-for:

Asset
~~~~~~~~~~

.. attributetable:: Asset
.. autoclass:: Asset()
    :members:

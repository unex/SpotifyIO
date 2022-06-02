from dataclasses import dataclass


@dataclass(slots=True)
class Scopes:
    # Images
    ugc_image_upload: bool = False
    # Spotify Connect
    user_modify_playback_state: bool = False
    user_read_playback_state: bool = False
    user_read_currently_playing: bool = False
    # Follow
    user_follow_modify: bool = False
    user_follow_read: bool = False
    # Listening History
    user_read_recently_played: bool = False
    user_read_playback_position: bool = False
    user_top_read: bool = False
    # Playlists
    playlist_read_collaborative: bool = False
    playlist_modify_public: bool = False
    playlist_read_private: bool = False
    playlist_modify_private: bool = False
    # Playback
    app_remote_control: bool = False
    streaming: bool = False
    # Users
    user_read_email: bool = False
    user_read_private: bool = False
    # Library
    user_library_modify: bool = False
    user_library_read: bool = False

    def __repr__(self) -> str:
        fields = ", ".join(
            [f"{k}=True" for k in self.__slots__ if getattr(self, k) == True]
        )
        return f"{self.__class__.__qualname__}({fields})"

    def __iter__(self) -> list:
        for k in self.__slots__:
            if getattr(self, k) == True:
                yield k.replace("_", "-")

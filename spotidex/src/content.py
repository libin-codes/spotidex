from spotidex.src.utils import *
from spotidex.src.static import *
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import SpotifyException
from requests import ConnectionError, ReadTimeout


class SpotifyContent:
    def __init__(self) -> None:
        client_cred_manager = SpotifyClientCredentials(client_id, client_secret)
        self.sp = Spotify(client_credentials_manager=client_cred_manager)

    def album_details(self, link):
        album_id = link.split("/")[-1].split("?")[0]
        try:
            album_data = self.sp.album(album_id)
        except (ConnectionError, ReadTimeout):
            raise SpotidexError("NetworkError")
        except SpotifyException:
            raise SpotidexError("InvalidSpotifyLink")

        details = {
            "album_name": album_data["name"],
            "album_type": album_data["album_type"],
            "total_tracks": album_data["tracks"]["total"],
            "release_date": album_data["release_date"],
            "label": album_data["label"],
            "image_url": album_data["images"][0]["url"],
            "track_details": [],
        }

        for offset in range(0, album_data["tracks"]["total"], 50):
            try:
                tracks = self.sp.album_tracks(album_id, offset=offset, limit=50)[
                    "items"
                ]
            except (ConnectionError, ReadTimeout):
                raise SpotidexError("NetworkError")
            except SpotifyException:
                raise SpotidexError("InvalidSpotifyLink")
            details["track_details"].extend(
                [
                    {
                        "track_name": track["name"],
                        "track_number": track["track_number"],
                        "disc_number": track["disc_number"],
                        "album": details["album_name"],
                        "artist": ", ".join(
                            [artist["name"] for artist in track["artists"]]
                        ),
                        "cover_image_url": (details["image_url"]),
                        "link": track["external_urls"]["spotify"],
                    }
                    for track in tracks
                ]
            )
        for track in details["track_details"]:
            if track["track_name"] == "":
                details["total_tracks"] -= 1
                details["track_details"].remove(track)

        return details

    def playlist_details(self, link):
        playlist_id = link.split("/")[-1].split("?")[0]
        try:
            playlist_data = self.sp.playlist(playlist_id)
        except (ConnectionError, ReadTimeout):
            raise SpotidexError("NetworkError")
        except SpotifyException:
            raise SpotidexError("InvalidSpotifyLink")

        details = {
            "playlist_name": playlist_data["name"],
            "description": playlist_data["description"],
            "creator": playlist_data["owner"]["display_name"],
            "followers": playlist_data["followers"]["total"],
            "total_tracks": playlist_data["tracks"]["total"],
            "image_url": playlist_data["images"][0]["url"],
            "track_details": [],
        }

        for offset in range(0, playlist_data["tracks"]["total"], 100):
            try:
                tracks = self.sp.playlist_items(playlist_id, offset=offset, limit=100)[
                    "items"
                ]
            except (ConnectionError, ReadTimeout):
                raise SpotidexError("NetworkError")
            except SpotifyException:
                raise SpotidexError("InvalidSpotifyLink")
            details["track_details"].extend(
                [
                    {
                        "track_name": track["track"]["name"],
                        "track_number": track["track"]["track_number"],
                        "disc_number": track["track"]["disc_number"],
                        "album": track["track"]["album"]["name"],
                        "artist": ", ".join(
                            [artist["name"] for artist in track["track"]["artists"]]
                        ),
                        "cover_image_url": (
                            track["track"]["album"]["images"][0]["url"]
                            if track["track"]["album"]["images"]
                            else None
                        ),
                        "link": track["track"]["external_urls"]["spotify"],
                    }
                    for track in tracks
                ]
            )
        for track in details["track_details"]:
            if track["track_name"] == "":
                details["total_tracks"] -= 1
                details["track_details"].remove(track)

        return details

    def track_details(self, link):
        try:
            track_data = self.sp.track(link.split("/")[-1].split("?")[0])
        except (ConnectionError, ReadTimeout):
            raise SpotidexError("NetworkError")
        except SpotifyException:
            raise SpotidexError("InvalidSpotifyLink")
        details = {
            "track_name": track_data["name"],
            "track_number": track_data["track_number"],
            "disc_number": track_data["disc_number"],
            "album": track_data["album"]["name"],
            "artist": ", ".join([artist["name"] for artist in track_data["artists"]]),
            "cover_image_url": (
                track_data["album"]["images"][0]["url"]
                if track_data["album"]["images"] != []
                else None
            ),
            "link": track_data["external_urls"]["spotify"],
        }

        return details

from spotidex.src.utils import *
from spotidex.src.static import *
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyContent:
    def __init__(self) -> None:
        client_cred_manager = SpotifyClientCredentials(client_id, client_secret)
        self.sp = Spotify(client_credentials_manager=client_cred_manager)

    def album_details(self, link):
        album_id = link.split("/")[-1].split("?")[0]
        album_data = self.sp.album(album_id)
        track_links = extract_track_links(self.sp,link)

        details = {
            "album_name": album_data["name"],
            "album_type": album_data["album_type"],
            "total_tracks": album_data["tracks"]["total"],
            "release_date": album_data["release_date"],
            "label": album_data["label"],
            "image_url": album_data["images"][0]["url"],
            "track_details":  parallel_searches(self,track_links),
        }

        return details

    def playlist_details(self, link):
        playlist_id = link.split("/")[-1].split("?")[0]
        playlist_data = self.sp.playlist(playlist_id)
        track_links = extract_track_links(self.sp, link)

        details = {
            "playlist_name": playlist_data["name"],
            "description": playlist_data["description"],
            "creator": playlist_data["owner"]["display_name"],
            "followers": playlist_data["followers"]["total"],
            "total_tracks": playlist_data["tracks"]["total"],
            "image_url": playlist_data["images"][0]["url"],
            "track_details": parallel_searches(self,track_links),
        }

        return details

    def track_details(self, link):
        track_data = self.sp.track(link.split("/")[-1].split("?")[0])

        details = {
            "track_name": track_data["name"],
            "track_number": track_data["track_number"],
            "disc_number": track_data["disc_number"],
            "album": track_data["album"]["name"],
            "artist": ", ".join([artist["name"] for artist in track_data["artists"]]),
            "cover_image_url": track_data["album"]["images"][0]["url"],
            "link": track_data["external_urls"]["spotify"],
        }

        return details

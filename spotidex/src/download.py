from spotidex.src.utils import *
from spotidex.src.static import *

from pathlib import Path

from tempfile import TemporaryDirectory
import shutil
import yt_dlp.YoutubeDL
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import SpotifyException
from requests import ConnectionError,ReadTimeout
from spotidex.src.content import SpotifyContent


class SpotifyDownloader:
    def __init__(self) -> None:
        self.spotidex_path = get_spotidex_data_directory()
        self.ffmpeg_path = get_ffmpeg()
        self.total_tracks = None
        self.sp = spotipy.Spotify(
            client_credentials_manager=
                SpotifyClientCredentials(
                    client_id,
                    client_secret,
            )
                )
        
    def _download_with_temp_directory(
        self,
        links,
        folder_name,
        custom_hook=None,
        download_path=Path.cwd(),
        quality="high",
        metadata=True,
        make_folder=True,
    ):
        with TemporaryDirectory(dir=str(self.spotidex_path)) as temp_folder:
            if make_folder:
                folder_name = get_valid_name(download_path, folder_name)
                temp_path = Path(temp_folder).joinpath(folder_name)
            else:
                temp_path = Path(temp_folder)

            done, not_done = pool_download(
                self, list(set(links)), custom_hook, temp_path, quality, metadata
            )
            if len(not_done) != 0:
                raise SpotidexError("NetworkError")
            progress_hook(self, {"status": "downloaded"}, custom_hook)
            for file_path in Path(temp_folder).iterdir():
                shutil.move(str(file_path), str(download_path))
            progress_hook(self, {"status": "transfered"}, custom_hook)
        

    def download_track(
        self,
        link,
        custom_hook=None,
        download_path=Path.cwd(),
        quality="high",
        metadata=True,
    ):
        try:
            data = self.sp.track(link.split("/")[-1].split("?")[0])
        except SpotifyException:
            raise SpotidexError("InvalidSpotifyLink")
        except (ConnectionError,ReadTimeout):
            raise SpotidexError("NetworkError")
        
        track_artist = ",".join([artist["name"] for artist in data["artists"]])
        query = data["name"]+f" song by {track_artist} official lyrics "
        file_name = get_valid_name(download_path,data["name"]+".mp3")
    
        with TemporaryDirectory(dir=str(self.spotidex_path)) as temp_folder:
            options = {
                "format": "bestaudio/best",
                "outtmpl": str(download_path)+'\\'+file_name,
                "quiet": True,
                "noprogress": True,
                "progress": "false",
                "ffmpeg_location": str(self.ffmpeg_path),
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": bitrate[quality],
                    }
                ],
                "retries": 20,
                "progress_hooks": [lambda d: progress_hook(self, d, custom_hook)]
                if custom_hook != None
                else [],
            }
                
            if self.total_tracks == None:
                options['outtmpl'] = str(Path(temp_folder))+'\\'+file_name
            ydl = yt_dlp.YoutubeDL(options)
            yt_video_result = ydl.extract_info(f"ytsearch:{query}", download=False)
            first_yt_video_link = yt_video_result["entries"][0]["webpage_url"]
            yt_video_download = ydl.extract_info(first_yt_video_link, download=True)
            downloaded_path = ydl.prepare_filename(yt_video_download)

            if metadata:
                add_metadata(data, Path(downloaded_path + ".mp3").resolve())

            if self.total_tracks == None:
                progress_hook(self, {"status": "downloaded"}, custom_hook)
                for file_path in Path(temp_folder).iterdir():
                    shutil.move(str(file_path), str(download_path))
                progress_hook(self, {"status": "transfered"}, custom_hook)
    
    def download_playlist(
        self,
        link,
        custom_hook=None,
        download_path=Path.cwd(),
        quality="high",
        metadata=True,
        make_folder=True,
    ):
        playlist_id = link.split("/")[-1].split("?")[0]
        try:
            playlist_data = SpotifyContent().playlist_details(playlist_id)
            track_links = [track["link"] for track in playlist_data['track_details']]
        except SpotifyException:
            raise SpotidexError("InvalidSpotifyLink")
        except (ConnectionError,ReadTimeout):
            raise SpotidexError("NetworkError")
        
        folder_name = get_valid_name(download_path,playlist_data['playlist_name'])

        self._download_with_temp_directory(
                track_links,
                folder_name,
                custom_hook,
                download_path,
                quality,
                metadata,
                make_folder,
            )
            
    def download_album(
        self,
        link,
        custom_hook=None,
        download_path=Path.cwd(),
        quality="high",
        metadata=True,
        make_folder=True,
    ):
        album_id = link.split("/")[-1].split("?")[0]
        try:
            album_data = SpotifyContent().album_details(album_id)
            track_links = [track["link"] for track in album_data['track_details']]
        except SpotifyException:
            raise SpotidexError("InvalidSpotifyLink")
        except (ConnectionError,ReadTimeout):
            raise SpotidexError("NetworkError")
        
        
        folder_name = get_valid_name(download_path,album_data['name'])
        
        self._download_with_temp_directory(
                track_links,
                folder_name,
                custom_hook,
                download_path,
                quality,
                metadata,
                make_folder,
            )
            
    def download_multiple_songs(
        self,
        links,
        folder_name,
        custom_hook=None,
        download_path=Path.cwd(),
        quality="high",
        metadata=True,
        make_folder=True,
    ):
        self._download_with_temp_directory(
                links,
                folder_name,
                custom_hook,
                download_path,
                quality,
                metadata,
                make_folder,
            )
            

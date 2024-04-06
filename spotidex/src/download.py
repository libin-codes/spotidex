from spotidex.src.utils import *
from spotidex.src.static import *

import re, logging
from pathlib import Path

from tempfile import TemporaryDirectory
import shutil
import yt_dlp.YoutubeDL
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyDownloader:
    def __init__(self) -> None:
        self.spotidex_path = get_spotidex_data_directory()
        self.ffmpeg_path = get_ffmpeg()
        self.is_library = False
        self.progress_dict = {}
        self.total_tracks = 1
   

        client_cred_manager = SpotifyClientCredentials(
            client_id,
            client_secret,
        )
        self.sp = Spotify(client_credentials_manager=client_cred_manager)
        

    def download_track(
        self,
        link,
        custom_hook=None,
        path=None,
        quality="high",
        metadata=True,
    ):
        logging.getLogger("pytube").setLevel(logging.ERROR)

        data = self.sp.track(link.split("/")[-1].split("?")[0])
        track_artist = ",".join([artist["name"] for artist in data["artists"]])
        track_name = data["name"]
        query = f"{track_name} song by {track_artist} official lyrics "

        file_name = re.sub(r"[^\w\d(),.\- ]", "", data["name"])
        download_path = Path.cwd() if path == None else path
        for i in range(1,1000000):
            if Path(download_path,file_name+".mp3").exists():
                file_name = file_name.split(" (")[0]+f" ({i})"
            else:
                break
        if self.is_library:
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

            ydl = yt_dlp.YoutubeDL(options)
            yt_video_result = ydl.extract_info(f"ytsearch:{query}", download=False)
            first_yt_video_link = yt_video_result["entries"][0]["webpage_url"]
            yt_video_download = ydl.extract_info(first_yt_video_link, download=True)
            downloaded_path = ydl.prepare_filename(yt_video_download)

            if metadata:
                add_metadata(data, Path(downloaded_path + ".mp3").resolve())
        else:
            with TemporaryDirectory(dir=str(self.spotidex_path)) as temp_folder:

                options = {
                    "format": "bestaudio/best",
                    "outtmpl": str(Path(temp_folder))+'\\'+file_name,
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

                ydl = yt_dlp.YoutubeDL(options)
                yt_video_result = ydl.extract_info(f"ytsearch:{query}", download=False)
                first_yt_video_link = yt_video_result["entries"][0]["webpage_url"]
                yt_video_download = ydl.extract_info(first_yt_video_link, download=True)
                downloaded_path = ydl.prepare_filename(yt_video_download)

                if metadata:
                    add_metadata(data, Path(downloaded_path + ".mp3").resolve())

                if not self.is_library and custom_hook is not None:
                    progress_hook(self, {"status": "downloaded"}, custom_hook)

                if not self.is_library:
                    for file_path in Path(temp_folder).iterdir():
                        shutil.move(file_path, download_path)

                    if custom_hook is not None:
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
        playlist_data = self.sp.playlist(playlist_id)
        track_links = extract_track_links(self.sp, link)

        self.is_library = True
        self.total_tracks = len(track_links)

        folder_name = re.sub(r"[^\w\d(),.\- ]", "", playlist_data["name"])
        for i in range(1,1000000):
            if Path(download_path,folder_name).exists():
                folder_name = folder_name.split(" (")[0]+f" ({i})"
            else:
                break
        with TemporaryDirectory(dir=str(self.spotidex_path)) as temp_folder:
            if make_folder == True:
                temp_path = Path(temp_folder).joinpath(folder_name)
            else:
                temp_path = Path(temp_folder)   

            done,not_done = pool_download(
                    self,
                    list(set(track_links)),
                    custom_hook,
                    temp_path,
                    quality,
                    metadata,
                )
            if len(not_done) != 0:
                raise ConnectionError
            
            if custom_hook != None:
                progress_hook(self, {"status": "downloaded"}, custom_hook)

            for file_path in Path(temp_folder).iterdir():
                shutil.move(str(file_path), str(download_path))

            if custom_hook != None:
                progress_hook(self, {"status": "transfered"}, custom_hook)
            
        


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
        album_data = self.sp.album(album_id)
        track_links = extract_track_links(self.sp, link)

        self.is_library = True
        self.total_tracks = len(track_links)
        
        folder_name,i = re.sub(r"[^\w\d(),.\-\[\] ]", "", folder_name),1
        while Path(download_path, folder_name).exists():
            folder_name,i = folder_name.split(" (")[0] + f" ({i})",i+1
        folder_name = re.sub(r"[^\w\d(),.\- ]", "", album_data["name"])
        for i in range(1,1000000):
            if Path(download_path,folder_name).exists():
                folder_name = folder_name.split(" (")[0]+f" ({i})"
            else:
                break
        with TemporaryDirectory(dir=str(self.spotidex_path)) as temp_folder:
            if make_folder == True:
                temp_path = Path(temp_folder).joinpath(folder_name)
            else:
                temp_path = Path(temp_folder)   

            done,not_done = pool_download(
                    self,
                    list(set(track_links)),
                    custom_hook,
                    temp_path,
                    quality,
                    metadata,
                )
            if len(not_done) != 0:
                raise ConnectionError

            progress_hook(self, {"status": "downloaded"}, custom_hook)
            with self.temp_folder:
                for file_path in Path(temp_folder).iterdir():
                    shutil.move(str(file_path), str(download_path))
            progress_hook(self, {"status": "transfered"}, custom_hook)
        


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
        self.is_library = True
        self.total_tracks = len(links)
        with TemporaryDirectory(dir=str(self.spotidex_path)) as temp_folder:
            if make_folder == True:
                folder_name,i = re.sub(r"[^\w\d(),.\-\[\] ]", "", folder_name),1
                while Path(download_path, folder_name).exists():
                    folder_name,i = folder_name.split(" (")[0] + f" ({i})",i+1
                temp_path = Path(temp_folder).joinpath(folder_name)
            else:
                temp_path = Path(temp_folder)   


            done,not_done = pool_download(
                    self, list(set(links)), custom_hook, temp_path, quality, metadata
                )
            if len(not_done) != 0:
                raise ConnectionError
            

            progress_hook(self, {"status": "downloaded"}, custom_hook)
            for file_path in Path(temp_folder).iterdir():
                shutil.move(str(file_path), str(download_path))
            progress_hook(self, {"status": "transfered"}, custom_hook)
        
    

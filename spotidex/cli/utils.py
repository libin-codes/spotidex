from spotidex import SpotifyContent
from spotidex import SpotifyDownloader
from pathlib import Path
import os
import shutil

scraper = SpotifyContent()


app_description = """[italic]Spotidex  \
is a cutting-edge powerful CLI app designed to enhance your Spotify experience. \
With an intuitive and user-friendly interface, \
Spotidex allows you to effortlessly download your favorite Spotify songs \
by simply pasting the Spotify link. Liberate your music and take it with \
you wherever you go, even when offline.

Spotidex supports a wide range of Spotify links, enabling \
users to download playlists, individual tracks, and entire albums effortlessly.

App's GitHub repository is available at [link=https://github.com/libin-codes/spotidex]https://github.com/libin-codes/spotidex[/link][/italic]
"""


def get_link_details(link):
    if "track" in link:
        track_details = scraper.track_details(link)
        return (
            {
                "TRACK ID": link.split("/")[-1].split("?")[0],
                "TRACK NAME": track_details["track_name"],
                "ARTIST": track_details["artist"],
                "ALBUM NAME": track_details["album"],
            },
        )

    elif "playlist" in link:
        playlist_details = scraper.playlist_details(link)
        return (
            {
                "PLAYLIST ID": link.split("/")[-1].split("?")[0],
                "PLAYLIST NAME": playlist_details["playlist_name"],
                "PLAYLIST CREATOR": playlist_details["creator"],
                "TOTAL TRACKS": str(playlist_details["total_tracks"]),
            },
            {
                track["track_name"]: track["link"]
                for track in playlist_details["track_details"]
            },
        )
    elif "album" in link:
        album_details = scraper.album_details(link)
        return (
            {
                "ALBUM ID": link.split("/")[-1].split("?")[0],
                "ALBUM NAME": album_details["album_name"],
                "RELEASE DATE": album_details["release_date"],
                "TOTAL TRACKS": str(album_details["total_tracks"]),
            },
            {
                track["track_name"]: track["link"]
                for track in album_details["track_details"]
            },
        )


def shorten_path(path: str, length):
    while len(path) > length:
        path_parts = path.split("\\") if os.name == "nt" else path.split("/")
        if "..." in path_parts:
            path_parts.pop(2)
        else:
            path_parts.pop(1)
            path_parts.insert(1, "...")
        path = "\\".join(path_parts) if os.name == "nt" else "/".join(path_parts)
    return path


def create_download_path(path, folder_name):
    folder_path = Path(path, folder_name)
    folder_path.mkdir(parents=True, exist_ok=True)

    return str(folder_path)


input_validator = lambda value: (
    True
    if ("spotify" in value)
    and (any(keyword in value for keyword in ["track", "playlist", "album"]))
    else False
)


def get_data_drive_path():
    if os.name != "nt":
        return "/"
    drives = [chr(_) for _ in list(range(ord("A"),ord("Z")+1))]
    drives.remove("C")
    available_drives = [
        drive + ":\\"
        for drive in drives
        if os.path.exists(drive + ":\\")
    ]
    return available_drives[0] if available_drives else None

def get_downloads_folder():
    home_dir = os.path.expanduser("~")
    downloads_folder = os.path.join(home_dir, "Downloads")

    return downloads_folder

def can_create_directory(path):
    try:
        os.mkdir(os.path.join(path,"temp826328ljij"))
        shutil.rmtree(os.path.join(path,"temp826328ljij"))
        return True
    
    except PermissionError:
        return False

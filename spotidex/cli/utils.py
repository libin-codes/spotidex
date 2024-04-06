
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
        path_parts = path.split("\\")
        if "..." in path_parts:
            path_parts.pop(2)
        else:
            path_parts.pop(1)
            path_parts.insert(1, "...")
        path = "\\".join(path_parts)
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
    # Get a list of all available drives
    drives = [chr(i) + ':' for i in range(ord('A'), ord('Z')+1)]

    # Iterate through the drives and find the one with the most available space
    max_free_space = 0
    data_drive_path = None
    for drive in drives:
        try:
            free_space = shutil.disk_usage(drive).free
            if free_space > max_free_space:
                max_free_space = free_space
                data_drive_path = os.path.join(drive, '/')
        except OSError:
            # Ignore drives that are not accessible
            pass

    if data_drive_path is None:
        raise ValueError("Data drive not found")

    return data_drive_path

def get_downloads_folder():
    # Get the user's home directory
    home_dir = os.path.expanduser("~")
    
    # Operating system specific logic to get the Downloads folder
    if os.name == 'posix':  # Unix-like OS (Linux, macOS)
        downloads_folder = os.path.join(home_dir, 'Downloads')
    elif os.name == 'nt':   # Windows
        downloads_folder = os.path.join(home_dir, 'Downloads')
    
    return downloads_folder
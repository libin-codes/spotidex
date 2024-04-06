import requests
from mutagen.id3 import ID3, APIC, TPE1, TIT2, TALB

from rich.panel import Panel
from rich.console import Console
from rich.table import Table
import os
import stat
import platform
from pathlib import Path
from spotidex.src.static import FFMPEG_URLS
from tqdm import tqdm
import concurrent.futures
import subprocess

console = Console()
clear_screen = lambda: print("\033c", end="")
validate_link = lambda link: True if "spotify.com" in link else False
validate_selection = lambda selected_songs: True if len(selected_songs) != 0 else False


def extract_track_links(sp, link):
    id = link.split("/")[-1].split("?")[0]
    if "playlist" in link:
        data = sp.playlist(id)
    elif "album" in link:
        data = sp.album(id)

    total_tracks = data["tracks"]["total"]
    offset, limit = 0, 100
    track_links = []

    while offset < total_tracks:
        if "playlist" in link:
            results = sp.playlist_items(id, offset=offset, limit=limit)
            for track in results["items"]:
                track_links.append(track["track"]["href"])

        elif "album" in link:
            limit = 40
            results = sp.album_tracks(id, offset=offset, limit=limit)
            for track in results["items"]:
                track_links.append(track["href"])

        offset += limit

    return track_links


def add_metadata(data, path):
    audio = ID3(path)
    audio.add(TIT2(encoding=3, text=data["name"]))
    audio.add(
        TPE1(encoding=3, text=",".join([artist["name"] for artist in data["artists"]]))
    )
    audio.add(TALB(encoding=3, text=data["album"]["name"]))
    audio.add(
        APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=requests.get(data["album"]["images"][0]["url"]).content,
        )
    )

    audio.save(v2_version=3)


def pool_download(
    downloader,
    links,
    custom_hook,
    download_path,
    quality,
    metadata,
    max_concurrent=4,
):
    with concurrent.futures.ThreadPoolExecutor(max_concurrent) as executor:
        tasks = [
            executor.submit(
                downloader.download_track,
                link,
                custom_hook,
                download_path,
                quality,
                metadata,
            )
            for link in links
        ]
        return concurrent.futures.wait(tasks,return_when="FIRST_EXCEPTION")


def progress_hook(self, d, custom_hook=None):
    if d["status"] == "downloading":
        percent = "".join(
            char for char in d["_percent_str"] if char.isdigit() or char == "."
        )
        if self.is_library:
            percent = "".join(
                char for char in d["_percent_str"] if char.isdigit() or char == "."
            )
            self.progress_dict.update(
                {d["info_dict"]["id"]: float(percent[3:]) * 0.943}
            )
            progress = sum(self.progress_dict.values()) / self.total_tracks
            custom_hook(str(round(progress, 1)))
        else:
            custom_hook(str(round(float(percent[3:]) * 0.943, 1)))
    elif d["status"] == "downloaded":
        custom_hook("97.8")
    elif d["status"] == "transfered":
        custom_hook("100")


def parallel_searches(self, track_links):
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        tasks = [executor.submit(self.track_details, link) for link in track_links]
        concurrent.futures.wait(tasks)
    return [task.result() for task in tasks]


def display_settings(settings):
    table = Table(
        title="[bold green]SETTINGS",
        show_header=False,
        row_styles=["yellow", "yellow", "yellow"],
        show_lines=True,
    )
    for i in settings.keys():
        table.add_row(i, settings[i])
    console.print(Panel(table, expand=False, border_style="blue"))


def display_table(dic: dict):
    title = {
        "ALBUM ID": "ALBUM INFO",
        "PLAYLIST ID": "PLAYLIST INFO",
        "TRACK ID": "TRACK INFO",
    }

    table = Table(
        title=f"[bold green]{title[list(dic.keys())[0]]}",
        show_header=False,
        row_styles=["yellow", "yellow", "yellow"],
        show_lines=True,
    )

    for i in dic.keys():
        table.add_row(i, str(dic[i]))
    console.print(Panel(table, expand=False, border_style="blue"))


def display_selected_songs(li):
    table = Table(
        title="[bold green]SELECTED SONGS",
        show_header=False,
        row_styles=["yellow", "yellow", "yellow"],
        show_lines=True,
    )
    table.add_column("Songs")
    for i in li:
        table.add_row(i)
    console.print(Panel(table, expand=False, border_style="blue"))


def get_spotidex_data_directory():
    spotidex_path = Path(os.path.expanduser("~"), ".spotidex")
    spotidex_path.mkdir(parents=True, exist_ok=True)

    return spotidex_path


def get_ffmpeg():
    os_name = platform.system().lower()
    os_arch = platform.machine().lower()

    ffmpeg_url = FFMPEG_URLS.get(os_name, {}).get(os_arch)
    ffmpeg_path = (
        get_spotidex_data_directory()
        / f"ffmpeg{''.join(('.exe' if os_name == 'windows' else ''))}"
    )

    if ffmpeg_path.exists():
        current_path = Path().cwd()
        os.chdir(get_spotidex_data_directory())
        try:
            subprocess.run(
                ["./ffmpeg.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception:
            try:
                ffmpeg_binary = requests.get(ffmpeg_url, stream=True, timeout=10)
            except Exception:
                print(
                    "Netowork Error: Please check your internet connction and try later"
                )
                exit()
            with open(ffmpeg_path, "wb") as ffmpeg_file, tqdm(
                total=100,
                unit="%",
                unit_scale=True,
                unit_divisor=1024,
                dynamic_ncols=True,
                bar_format="Initializing : |{bar:50}| {percentage:.0f}% ",
            ) as progress_bar:
                try:
                    for data in ffmpeg_binary.iter_content(chunk_size=1024):
                        ffmpeg_file.write(data)
                        progress_bar.update(
                            len(data)
                            * 100
                            / int(ffmpeg_binary.headers.get("content-length", 0))
                        )
                except Exception:
                    progress_bar.close()
                    print(
                        "Netowork Error: Please check your internet connction and try later"
                    )
                    exit()
            if os_name in ["linux", "darwin"]:
                ffmpeg_path.chmod(ffmpeg_path.stat().st_mode | stat.S_IEXEC)
            os.chdir(current_path)
            return ffmpeg_path
        os.chdir(current_path)
        return ffmpeg_path

    try:
        ffmpeg_binary = requests.get(ffmpeg_url, stream=True, timeout=10)
    except Exception:
        print("Netowork Error: Please check your internet connction and try later")
        exit()

    with open(ffmpeg_path, "wb") as ffmpeg_file, tqdm(
        total=100,
        unit="%",
        unit_scale=True,
        unit_divisor=1024,
        dynamic_ncols=True,
        bar_format="Initializing : |{bar:50}| {percentage:.0f}% ",
    ) as progress_bar:

        try:
            for data in ffmpeg_binary.iter_content(chunk_size=1024):
                ffmpeg_file.write(data)
                progress_bar.update(
                    len(data)
                    * 100
                    / int(ffmpeg_binary.headers.get("content-length", 0))
                )
        except Exception:
            progress_bar.close()
            print("Netowork Error: Please check your internet connction and try later")
            exit()

    if os_name in ["linux", "darwin"]:
        ffmpeg_path.chmod(ffmpeg_path.stat().st_mode | stat.S_IEXEC)

    return ffmpeg_path

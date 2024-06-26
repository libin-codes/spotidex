import os, re, stat, platform, requests, subprocess ,shutil
from mutagen.id3 import ID3, APIC, TPE1, TIT2, TALB
import concurrent.futures
from pathlib import Path
from rich.progress import Progress, SpinnerColumn

from spotidex.src.static import FFMPEG_URLS

progress_dict = {}

class SpotidexError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

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
    downloader.total_tracks = len(links)
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
        return concurrent.futures.wait(tasks)


def progress_hook(self, d, custom_hook=None):
    global progress_dict
    if custom_hook is None:
        return
    if d["status"] == "downloading":
        percent = "".join(
            char for char in d["_percent_str"] if char.isdigit() or char == "."
        )
        if self.total_tracks != None:
            progress_dict.update({d["info_dict"]["id"]: float(percent[3:]) * 0.943})
            progress = sum(progress_dict.values()) / self.total_tracks
            custom_hook(str(round(progress, 1)))
        else:
            custom_hook(str(round(float(percent[3:]) * 0.943, 1)))
    elif d["status"] == "downloaded":
        custom_hook("97.8")
    elif d["status"] == "transfered":
        custom_hook("100")
        progress_dict = {}
        self.total_tracks = None

def get_spotidex_data_directory():
    spotidex_path = Path(os.path.expanduser("~"), ".spotidex")
    spotidex_path.mkdir(parents=True, exist_ok=True)
    return spotidex_path


def get_ffmpeg():
    os_name = platform.system().lower()
    os_arch = platform.machine().lower()

    ffmpeg_url = FFMPEG_URLS.get(os_name, {}).get(os_arch)
    ffmpeg_path = get_ffmpeg_path(os_name)

    if ffmpeg_path.exists():
        if not run_ffmpeg(ffmpeg_path):
            download_ffmpeg(ffmpeg_url, ffmpeg_path, os_name)
        return ffmpeg_path

    download_ffmpeg(ffmpeg_url, ffmpeg_path, os_name)
    return ffmpeg_path


def get_ffmpeg_path(os_name):
    executable_extension = ".exe" if os_name == "windows" else ""
    return get_spotidex_data_directory() / f"ffmpeg{executable_extension}"


def run_ffmpeg(ffmpeg_path):
    current_path = Path().cwd()
    os.chdir(get_spotidex_data_directory())
    try:
        subprocess.run(
            [ffmpeg_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except Exception:
        return False
    os.chdir(current_path)
    return True


def download_ffmpeg(ffmpeg_url, ffmpeg_path, os_name):
    try:
        ffmpeg_binary = requests.get(ffmpeg_url, stream=True, timeout=10)
    except Exception:
        print("Network Error: Please check your internet connection and try later")
        exit()
    with open(ffmpeg_path, "wb") as ffmpeg_file:
        try:
            total_length = int(ffmpeg_binary.headers.get("content-length", 0))
            with Progress(
                SpinnerColumn("arc"),
                " INITIALIZING{task.percentage:>3.0f}%",
            ) as progress:
                task = progress.add_task("Downloading", total=total_length)
                for data in ffmpeg_binary.iter_content(chunk_size=1024):
                    ffmpeg_file.write(data)
                    progress.update(task, advance=len(data), total_bytes=total_length)
        except Exception as e:
            print("Network Error: Please check your internet connection and try later")
            exit()

    if os_name in ["linux", "darwin"]:
        ffmpeg_path.chmod(ffmpeg_path.stat().st_mode | stat.S_IEXEC)

def get_valid_name(path, name):
    name, i = re.sub(r"[^\w\d(),.\-\[\] ]", "", name), 1
    add_mp3 = ".mp3" if ".mp3" in name else ""
    while Path(path, name).exists():
        name, i = (
            (name.replace(".mp3", "") + f" ({i})" + add_mp3, i + 1)
            if i == 1
            else (name.replace('.mp3',"")[::-1].split("(",1)[-1][::-1] + f"({i})" + add_mp3, i + 1)
        )

    return name.replace(".mp3", "")

def delete_temp_folders():
    directory = get_spotidex_data_directory()
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
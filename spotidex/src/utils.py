import os,re,stat,platform,requests,subprocess
from mutagen.id3 import ID3, APIC, TPE1, TIT2, TALB
import concurrent.futures
from pathlib import Path
from tqdm import tqdm

from spotidex.src.static import FFMPEG_URLS

progress_dict = {}
class SpotidexError(Exception):
    def __init__(self,message):
        self.message = message
        super().__init__(message)

def extract_track_links(sp, link):
    id = link.split("/")[-1].split("?")[0]
    is_playlist = "playlist" in link
    data = sp.playlist(id) if is_playlist else sp.album(id)
    total_tracks = data["tracks"]["total"]
    offset, limit = 0, 100 if is_playlist else 40
    track_links = []

    while offset < total_tracks:
        results = (
            sp.playlist_items(id, offset=offset, limit=limit)
            if is_playlist
            else sp.album_tracks(id, offset=offset, limit=limit)
        )
        for track in results["items"]:
            track_links.append(track["track"]["href"] if is_playlist else track["href"])
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
            progress_dict.update(
                {d["info_dict"]["id"]: float(percent[3:]) * 0.943}
            )
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


def parallel_searches(self, track_links):
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        tasks = [executor.submit(self.track_details, link) for link in track_links]
        concurrent.futures.wait(tasks)
    return [task.result() for task in tasks]


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
        run_ffmpeg(ffmpeg_path)
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
        print("Network Error: Please check your internet connection and try later")
        exit()
    finally:
        os.chdir(current_path)


def download_ffmpeg(ffmpeg_url, ffmpeg_path, os_name):
    try:
        ffmpeg_binary = requests.get(ffmpeg_url, stream=True, timeout=10)
    except Exception:
        print("Network Error: Please check your internet connection and try later")
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
            print("Network Error: Please check your internet connection and try later")
            exit()

    if os_name in ["linux", "darwin"]:
        ffmpeg_path.chmod(ffmpeg_path.stat().st_mode | stat.S_IEXEC)

def get_valid_name(path, name):
    name, i = re.sub(r"[^\w\d(),.\-\[\] ]", "", name), 1
    add_mp3 = ".mp3" if ".mp3" in name else ""
    while Path(path, name).exists():
        name, i = name.replace('.mp3',"").split(" (")[0] + f" ({i})" + add_mp3, i + 1
    return name.replace('.mp3',"")

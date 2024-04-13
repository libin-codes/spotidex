

from textual.widgets import Static, RichLog, Label, ProgressBar
from textual.containers import Horizontal
from textual.screen import Screen
from textual.app import App

from rich.table import Table
from rich.align import Align

from spotidex.cli.utils import Path,SpotifyDownloader

from spotidex.cli.custom_widgets.AppInterface import AppInterface
from spotidex.cli.utils import shorten_path
from textual import work
from textual.worker import Worker, get_current_worker
from spotidex.cli.popup_screens.NetworkErrorPopup import NetworkErrorScreen

CSS = """

Download{
    align:center middle;

}

#download-interface #interface{
    padding: 1 3;
    grid-rows:1fr 5;
    grid-gutter: 1 1;
}

#music-info{
    width:95;
   
}


#info-container{
    border: heavy ansi_bright_green;
    border-title-align: center;
    content-align:center middle;
    padding-left:1;
 
}

#progress-bar-container{
    width:90;
    height:5;
    background:$boost;
    padding-right:1;

    
}
#progress{
    width:16;
    height:5;
    background:$boost;
    content-align:center middle;
    text-style: bold;
}



#bc{
    height:3;
    margin-top:1;
    margin-left:3;
    margin-right:2;
    padding-top:1;
    padding-left:4;
    background:$boost;
}

#stat{
    width:14;
}
"""


class Download(Screen):
    DEFAULT_CSS = CSS

    def compose(self):
        yield AppInterface(
            Horizontal(RichLog(id="music-info"), id="info-container"),
            Horizontal(
                Label("PROGRESS", id="progress"),
                Horizontal(
                    Static("DOWNLOADING : ", id="stat"), ProgressBar(id="bar"), id="bc"
                ),
                id="progress-bar-container",
            ),
            id="download-interface",
        )

    def on_mount(self):
        self.app.query_one("#nav-label").update("[bold]DOWNLOAD INTERFACE")
        text_log = self.app.query_one("#music-info")
        text_log.clear()

        table = Table(
            show_header=False, row_styles=["yellow"] * 3, width=85, show_lines=True
        )
        if "track" in self.app.spotify_link:
            link_type = "TRACK"
        elif "playlist" in self.app.spotify_link:
            link_type = "PLAYLIST"
        elif "album" in self.app.spotify_link:
            link_type = "ALBUM"

        self.query_one("#info-container").border_title = "DOWNLOAD INFO"
        name = self.app.link_details[0][f"{link_type} NAME"]

        if "track" in self.app.spotify_link:
            full_track_info = f"{name} by {self.app.link_details[0]['ARTIST']}"
            track_info = (
                full_track_info[:57] + "..."
                if len(full_track_info) > 57
                else (name[:57] + "..." if len(name) > 40 else full_track_info)
            )
        else:
            track_info = (
                f"{name[:43]}... [{len(self.app.selected_tracks)} Tracks]"
                if len(name) > 43
                else f"{name} [{len(self.app.selected_tracks)} Tracks]"
            )

        download_info = {
            f"{link_type.capitalize()} Info": track_info,
            "Download Path": shorten_path(self.app.saved_settings["download_path"], 57),
            "Download Quality": self.app.saved_settings["download_quality"],
            "Include Metadata": str(self.app.saved_settings["add_metadata"]),
        }

        for key, value in download_info.items():
            table.add_row(Align(key, align="center"), Align(value, align="center"))

        text_log.write(table)
        self.app.query_one("#back-button").label = "GO HOME"
        self.app.query_one("#back-button").disabled = True
        self.app.query_one("#exit-button").disabled = True
        self.download_music()

    def progress_hook(self, percent):
        if self.app.query_one("ProgressBar").percentage != 0.0:
            self.app.query_one("ProgressBar").update(total=100)
        self.app.query_one("ProgressBar",ProgressBar).update(progress=float(percent))

    def on_worker_state_changed(self, event) -> None:
        def eval(value):
            if value == "retry":
                self.app.query_one("ProgressBar",ProgressBar).update(progress=0, total=None)
                self.download_music()

        if str(event.state) == "WorkerState.CANCELLED":
            self.app.push_screen(NetworkErrorScreen(), eval)

    @work(thread=True, exclusive=True)
    def download_music(self):
        try:
            if "track" in self.app.spotify_link:
                SpotifyDownloader().download_track(
                    self.app.spotify_link,
                    self.progress_hook,
                    self.app.saved_settings["download_path"],
                    self.app.saved_settings["download_quality"],
                    self.app.saved_settings["add_metadata"],
                )
            elif self.app.selected_tracks == self.app.link_details[1].keys():
                if "playlist" in self.app.spotify_link:
                    SpotifyDownloader().download_playlist(
                        self.app.spotify_link,
                        self.progress_hook,
                        self.app.saved_settings["download_path"],
                        self.app.saved_settings["download_quality"],
                        self.app.saved_settings["add_metadata"],
                    )
                elif "album" in self.app.spotify_link:
                    SpotifyDownloader().download_album(
                        self.app.spotify_link,
                        self.progress_hook,
                        self.app.saved_settings["download_path"],
                        self.app.saved_settings["download_quality"],
                        self.app.saved_settings["add_metadata"],
                    )
            else:
                if "playlist" in self.app.spotify_link:
                    folder_name = self.app.link_details[0]["PLAYLIST NAME"]
                elif "album" in self.app.spotify_link:
                    folder_name = self.app.link_details[0]["ALBUM NAME"]
                SpotifyDownloader().download_multiple_songs(
                    self.app.selected_tracks,
                    f"{folder_name} [{len(self.app.selected_tracks)} Tracks]",
                    self.progress_hook,
                    self.app.saved_settings["download_path"],
                    self.app.saved_settings["download_quality"],
                    self.app.saved_settings["add_metadata"],
                )
            self.app.query_one("#stat").update("DOWNLOADED : ")
            self.app.query_one("#back-button").disabled = False
            self.app.query_one("#exit-button").disabled = False
        except Exception:
            get_current_worker().cancel()

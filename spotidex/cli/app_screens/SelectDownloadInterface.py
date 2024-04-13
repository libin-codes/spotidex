
from textual.widgets import Button, Static, Checkbox
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen

from spotidex.cli.custom_widgets.AppInterface import AppInterface
from spotidex.cli.app_screens.DownloadInterface import Download

CSS = """
SelectDownload{
    align:center middle;


}
#interface{
    padding:1 1;
}

#all-tracks {
    border:tall $boost;
    border-title-align: center;
    width: 63;
    height: 100%;
    background: $boost;
    padding-left:1;
    padding-right:1;
    margin-left:1;
}


#selectsongs-label{
    dock:right;
    margin-right: 15;
}

#selected-tracks-buttons-container{
    dock:right;
    width: 27;
}

#deselect-all-button{

    margin-top: 1;
    width: 25;
    margin-left: 1;
}

#select-all-button{
    width: 25;
    margin-top: 1;
    margin-left: 1;
}

#download-selected-button{
    width: 25;
    margin-top: 1;
    margin-left: 1;
}

#selected-tracks-label{
    width:27;
    height: 3;
    border:tall $boost;
    background:$boost;
    content-align:center middle;
    margin-bottom:2;

}



.all-songs-checkbox {
    width:56;
    padding-right:3;
}
.all-songs-checkbox:hover {
    text-style:none;
    opacity:0.8;
}
.all-songs-checkbox.-on{
    border: tall transparent;
    background:#32CD32;
    opacity:0.5;
}

.all-songs-checkbox:focus > .toggle--label {
    text-style: none;
    margin-left:0;
}

.all-songs-checkbox:focus {
    border:tall transparent
}

"""


class SelectDownload(Screen):
    DEFAULT_CSS = CSS
    selected_tracks = []

    def __init__(self):
        self.tracks = self.app.link_details[1]
        super().__init__()

    def compose(self):
        yield AppInterface(
            Horizontal(VerticalScroll(id="all-tracks"), id="all-tracks-container"),
            Vertical(
                Static("SELECTED TRACKS : 0", id="selected-tracks-label"),
                Button("DESELECT ALL", "error", id="deselect-all-button"),
                Button("SELECT ALL", "primary", id="select-all-button"),
                Button("DOWNLOAD SELECTED ", "success", id="download-selected-button",disabled=True),
                id="selected-tracks-buttons-container",
            ),
        )

    def on_checkbox_changed(self) -> None:
        selected_songs = []
        for checkbox in self.app.query(".all-songs-checkbox"):
            if checkbox.value == True:
                selected_songs.append(str(checkbox.label).split(". ",maxsplit=1)[1])
        self.app.query_one("#selected-tracks-label").update(
            f"SELECTED TRACKS : {len(selected_songs)}"
        )
        self.app.selected_tracks = [self.tracks[song] for song in selected_songs]
        if len(self.app.selected_tracks) != 0 :
            self.query_one('#download-selected-button').disabled = False
        else:
            self.query_one('#download-selected-button').disabled = True

    def on_mount(self):
        self.app.query_one("#nav-label").update("[bold]SELECT TRACKS TO DOWNLOAD")
        for song, track_no in zip(
            self.tracks.keys(), range(1, len(self.tracks.keys()) + 1)
        ):
            self.app.query_one("#all-tracks").mount(
                Checkbox(f"{track_no}. " + song, classes="all-songs-checkbox")
            )
        for i in self.app.query(".all-songs-checkbox"):
            i.BUTTON_INNER = ""
            i.BUTTON_LEFT = ""
            i.BUTTON_RIGHT = ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "deselect-all-button":
            for checkbox in self.app.query(".all-songs-checkbox"):
                checkbox.value = False
        elif event.button.id == "select-all-button":
            for checkbox in self.app.query(".all-songs-checkbox"):
                checkbox.value = True
        elif event.button.id == "download-selected-button":
            self.app.push_screen(Download())

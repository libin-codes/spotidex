from textual.widgets import RichLog, Button
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Header,Footer

from spotidex.cli.utils import  Path

from rich.table import Table
from rich.align import Align

from spotidex.cli.custom_widgets.AppInterface import AppInterface
from spotidex.cli.app_screens.SelectDownloadInterface import SelectDownload
from spotidex.cli.app_screens.DownloadInterface import Download



CSS = """

MainMenuInterface{
    align:center middle;
}

#main-menu-interface #interface{
    padding: 2 5;
    grid-rows:1fr 3;
    grid-gutter: 1 1;
    
}

#link-info-container{
    width: 84;
    border: heavy ansi_bright_magenta;
    border-title-align: center;
    content-align:center middle;
    padding-left:1;
}

#link-info{
    width: 86;
    background:transparent;
}

#download-button{
    width:100%;
    column-span:1;
}

#download-all-button{
    width:100%
}

#select-download-button{
    width:100%;
}

#settings-button{
    width:98%;
    column-span:1;
}


"""


class MainMenuInterface(Screen):
    DEFAULT_CSS = CSS

    def __init__(self) -> None:
        self.spotify_link = self.app.spotify_link
        self.link_details = self.app.link_details
        self.app.selected_tracks = []
        self.app.install_screen(SelectDownload, "SelectDownloadScreen")
        super().__init__()

    def compose(self):
        childrens = [
            Container(
                RichLog(
                    highlight=True,
                    markup=True,
                    id="link-info",
                    auto_scroll=False,
                ),
                id="link-info-container",
            ),
            Button("SETTINGS", "primary", id="settings-button"),
        ]
        if "track" not in self.spotify_link:
            childrens.insert(
                1, Button("DOWNLOAD ALL TRACK", "success", id="download-all-button")
            )
            childrens.insert(
                2, Button("SELECT TO DOWNLOAD", "success", id="select-download-button")
            )
        else:
            childrens.insert(
                1, Button("DOWNLOAD TRACK", "success", id="download-button")
            )

        yield AppInterface(*childrens, id="main-menu-interface")
  
    def on_mount(self):
        link_info = self.link_details[0]
        text_log = self.query_one("#link-info")

        if "track" in self.spotify_link:
            self.query_one("#link-info-container").border_title = "TRACK INFO"
        elif "playlist" in self.spotify_link:
            self.query_one("#link-info-container").border_title = "PLAYLIST INFO"
        else:
            self.query_one("#link-info-container").border_title = "ALBUM INFO"

        text_log.clear()
        table = Table(
            show_header=False,
            row_styles=["yellow", "yellow", "yellow"],
            width=80,
            show_lines=True,
        )

        for i in link_info:
            table.add_row(
                Align(i, align="center"),
                Align(
                    (
                        link_info[i][:60] + "..."
                        if len(link_info[i]) > 60
                        else link_info[i]
                    ),
                    align="center",
                ),
            )
        text_log.write(table)

        self.app.query_one("#nav-label").update("[bold]MAIN MENU")
        if "track" in self.spotify_link:
            self.query_one("#interface").styles.grid_size_columns = 2
            self.query_one("#link-info-container").styles.column_span = 2
            self.query_one("#interface").styles.grid_gutter_vertical = 3

        else:
            self.query_one("#interface").styles.grid_size_columns = 3
            self.query_one("#link-info-container").styles.column_span = 3
            self.query_one("#interface").styles.grid_gutter_vertical = 2

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download-button":
            self.app.push_screen(Download())
        elif event.button.id == "download-all-button":
            self.app.push_screen(Download())
            self.app.selected_tracks = self.link_details[1].keys()
        elif event.button.id == "select-download-button":
            self.app.push_screen("SelectDownloadScreen")
        elif event.button.id == "settings-button":
            self.app.push_screen("SettingsScreen")

        self.app.mount(Header(show_clock=True))
        self.app.mount(Footer())

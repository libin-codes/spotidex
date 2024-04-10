from textual.widgets import Button, Static
from textual.containers import Container
from textual.widget import Widget

from spotidex.cli.popup_screens.DownloadPathPopup import DownloadPathScreen
from spotidex.cli.utils import Path, shorten_path, get_downloads_folder
from textual.reactive import reactive

CSS = """
DownloadPathSelector{
    width:auto;
    height:auto;

}

#download-path-container{
    layout:horizontal;
    width:87;
    height: auto;
    padding:1;
    background:$boost;
}


#download-path-button{
    min-width:12;
    margin-left:1;
}

#download-path-label{
    background:$boost;
    width:71;
    height:3;
    border:tall $primary;
    padding-left:1;
}

"""


class DownloadPathSelector(Widget):
    DEFAULT_CSS = CSS
    value = reactive(str(get_downloads_folder()))

    def compose(self):
        with Container(id="download-path-container"):
            yield Static(id="download-path-label")
            yield Button("CHANGE", id="download-path-button", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        def change_value(value):
            self.value = value

        if event.button.id == "download-path-button":
            self.app.push_screen(DownloadPathScreen(), change_value)

    def watch_value(self, value):
        self.query_one("#download-path-label").update(
            "[bold]" + shorten_path(value, 65)
        )

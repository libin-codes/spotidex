from textual.widgets import Button
from textual.containers import Horizontal
from textual.screen import Screen
from textual.reactive import reactive

from spotidex.cli.custom_widgets.DownloadPathSelector import DownloadPathSelector
from spotidex.cli.custom_widgets.MetadataCheckBox import MetadataCheckBox
from spotidex.cli.custom_widgets.DownloadQualitySelection import DownloadQualitySelection
from spotidex.cli.custom_widgets.AppInterface import AppInterface
from spotidex.cli.utils import Path

CSS = """
Settings{
    align:center middle;
    height:auto;
    width:auto;

}

#settings-interface #interface{
    grid-size:2 3;
    padding:1 4;
    grid-gutter:1 2;
    align:center middle;
}
DownloadPathSelector{
    column-span:2;
}
DownloadQualitySelection{
    dock:right;
}

#metadata-download-quality-container{
    column-span:2;
}
#save-settings-button{
    width:100%;
}
#reset-settings-button{
    width:100%;
    
}
"""


class Settings(Screen):
    DEFAULT_CSS = CSS

    def compose(self):
        yield AppInterface(
            DownloadPathSelector(),
            Horizontal(
                MetadataCheckBox(),
                DownloadQualitySelection(),
                id="metadata-download-quality-container",
            ),
            Button("SAVE SETTINGS", "success", id="save-settings-button"),
            Button("RESET SETTINGS", "error", id="reset-settings-button"),
            id = "settings-interface"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "reset-settings-button":
            self.app.query_one(MetadataCheckBox).value = True
            self.app.query_one(DownloadPathSelector).value = str(Path.cwd())
            self.app.query_one(DownloadQualitySelection).value = "high"
        elif event.button.id == "save-settings-button":
            self.app.notify("SETTINGS SAVED SUCCESSFULLY", title="Spotidex")
            self.app.saved_settings = {
                "add_metadata":self.app.query_one(MetadataCheckBox).value ,
                "download_path": self.app.query_one(DownloadPathSelector).value,
                "download_quality": self.app.query_one(DownloadQualitySelection).value,
                }
            self.app.pop_screen()
            
    def on_mount(self):
        self.app.query_one("#nav-label").update('[bold]SETTINGS')


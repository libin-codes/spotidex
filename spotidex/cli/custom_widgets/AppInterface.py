from textual.app import ComposeResult
from textual.containers import Container
from textual.events import Mount
from textual.widgets import Label, Button, Static, Input,Header,Footer
from textual.widget import Widget
from textual.containers import Grid
from textual.reactive import reactive

from spotidex.cli.popup_screens.GoBackSettingsPopup import GoBackSettings
from spotidex.cli.popup_screens.ExitScreenPopup import ExitScreen


CSS = """
AppInterface{
    height:auto;
    width:auto;

}

#interface {
    background:$boost;
    height:19 ;
    width:95 ;
    margin-top: 1;
  
}
#loading-interface{
    background:$boost;
    height:19 ;
    width:95 ;
    margin-top: 1;
}

#app-container{
    width:99;
    height:27;
    background: $background 90% ;
    padding:1 2;
}

#appheader-container{
    layout:horizontal;
    background:$boost;
    height:5;
    width:95 ;
    padding: 1;
}

#nav-label-container{
    align:center middle;

}

#nav-label{
    color:gainsboro;
}

#back-button{
    dock:left;
    margin-left:2;
}

#exit-button{
    dock:right;
    margin-right:2;
}

"""


class AppHeader(Static):
    DEFAULT_CSS = CSS

    def compose(self):
        with Container(id="appheader-container"):
            yield Button("GO BACK", id="back-button")
            with Container(id="nav-label-container"):
                yield Label(id="nav-label")
            yield Button("EXIT", id="exit-button")

    def eval_settings(self, value):
        settings = self.app.saved_settings
        if value:
            self.app.notify("SETTINGS SAVED SUCCESSFULLY", title="Spotidex")
            self.app.saved_settings = {
                "add_metadata": self.app.query_one("MetadataCheckBox").value,
                "download_path": self.app.query_one("DownloadPathSelector").value,
                "download_quality": self.app.query_one(
                    "DownloadQualitySelection"
                ).value,
            }
        else:
            self.app.query_one("MetadataCheckBox").value = settings["add_metadata"]
            self.app.query_one("DownloadPathSelector").value = settings["download_path"]
            self.app.query_one("DownloadQualitySelection").value = settings[
                "download_quality"
            ]
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:

        if event.button.id == "exit-button":
            self.app.push_screen(ExitScreen())

        elif event.button.id == "back-button":
            if str(self.app.screen) == "Settings()":
                settings = self.app.saved_settings
                if (
                    (
                        self.app.query_one("MetadataCheckBox").value
                        != settings["add_metadata"]
                    )
                    or (
                        self.app.query_one("DownloadPathSelector").value
                        != settings["download_path"]
                    )
                    or (
                        self.app.query_one("DownloadQualitySelection").value
                        != settings["download_quality"]
                    )
                ):
                    self.app.push_screen(GoBackSettings(), self.eval_settings)
                else:
                    self.app.pop_screen()
            elif str(self.app.screen) == "MainMenuInterface()":
                self.app.pop_screen()
                self.app.query_one("#search-input").value = ""
                self.app.uninstall_screen("SelectDownloadScreen")

            elif str(self.app.screen) == "Download()":

                for _ in range(len(self.app.screen_stack) - 2):
                    self.app.pop_screen()
                self.app.query_one("#search-input", Input).clear()
                self.app.uninstall_screen("SelectDownloadScreen")

            else:
                self.app.pop_screen()


class AppInterface(Widget):
    DEFAULT_CSS = CSS

    def __init__(self, *children, disabled: bool = False, id=None) -> None:
        self.childrens = children
        super().__init__(disabled=disabled, id=id)

    def compose(self):
     
        with Container(id="app-container"):
            yield AppHeader()
            yield Grid(*self.childrens, id="interface")

    def on_mount(self):
        self.app.mount(Header(show_clock=True))
        self.app.mount(Footer())

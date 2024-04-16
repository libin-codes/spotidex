from textual.widgets import Input, Button, Label
from textual.screen import Screen
from textual.containers import Horizontal

from spotidex.cli.custom_widgets.AppInterface import AppInterface
from spotidex.cli.app_screens.MainMenuInterface import MainMenuInterface
from spotidex.src.utils import SpotidexError
from spotidex.cli.utils import input_validator, app_description
from spotidex.cli.utils import get_link_details

from textual.worker import Worker, get_current_worker
from textual.binding import Binding
from textual import work
import pyperclip

CSS = """
Search {
    align: center middle;
}

#search-interface #interface{
    grid-size:1 2;
    grid-rows:3 1fr;
    grid-gutter:1;
    padding: 2 3 0 3;
    
}

#search-input{
    column-span:1;
    width: 74%;
}

#search-button{
    column-span:1;
    width: 23%;
    margin-left:1;
}

#app-description{
    border:heavy ansi_bright_blue 80%;
    border-title-align: center;
    padding-left:1;

}

#search-input:blur{
    border:tall black
}
"""


class Search(Screen):
    DEFAULT_CSS = CSS
    BINDINGS = [
        Binding("tab", "paste_link", "PASTE SPOTIFY LINK", priority=True),
        Binding("delete", "clear_input", "CLEAR INPUT", priority=True),
    ]

    def compose(self):
        yield AppInterface(
            Horizontal(
                Input(
                    id="search-input",
                    placeholder="PASTE YOUR SPOTIFY LINK HERE",
                ),
                Button("SEARCH", "success", id="search-button", disabled=True),
            ),
            Label(app_description, id="app-description", shrink=True),
            id="search-interface",
        )

    def action_paste_link(self):
        if self.query_one("#search-input", Input).value == "":
            self.query_one("#search-input", Input).value = pyperclip.paste()
        self.query_one("#search-input", Input).focus()

    def action_clear_input(self):
        self.query_one("#search-input", Input).value = ""

    @work(exclusive=True, thread=True)
    def get_link_info(self):
        self.app.query_one("LoadingIndicator").styles.background = "#1c1c1c"
        try:
            self.app.link_details = get_link_details(self.app.spotify_link)
            if (
                "track" not in self.app.spotify_link
                and int(self.app.link_details[0]["TOTAL TRACKS"]) > 100
            ):
                raise SpotidexError("Maxlimit")

        except Exception as spotidex_error:
            if spotidex_error.message == "NetworkError":
                self.app.notify(
                    "Please check you internet connection and try again",
                    title="Network Error",
                    severity="error",
                )
            elif spotidex_error.message == "InvalidSpotifyLink":
                self.app.notify(
                    "The link provided is not valid, please check the link and try again",
                    title="INVALID LINK",
                    severity="error",
                )
            elif spotidex_error.message == "Maxlimit":
                self.query_one("#search-input").value = ""
                self.app.notify(
                    "The total track of playlist/album has exceeded the maximum limit which is 100",
                    title="MAX LIMIT REACHED",
                    severity="error",
                )

            get_current_worker().cancel()
        self.app.query_one("#interface").loading = False
        self.app.query_one("#exit-button").disabled = False
        self.app.query_one("#interface").styles.padding = (2, 3, 0, 3)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if str(event.state) == "WorkerState.CANCELLED":
            self.query_one("#search-input").visible = True
            self.query_one("#app-description").visible = True
            self.query_one("#search-button").visible = True
        elif str(event.state) == "WorkerState.SUCCESS":
            self.app.push_screen(MainMenuInterface())
            self.query_one("#search-input").visible = True
            self.query_one("#app-description").visible = True
            self.query_one("#search-button").visible = True
            self.query_one("#search-button").disabled = True

    def on_mount(self):
        self.app.query_one("#nav-label").update("[bold]HOME")
        self.query_one("#app-description").border_title = "ABOUT SPOTIDEX"
        self.app.query_one("#back-button").disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "search-button":
            self.app.query_one("#interface").styles.padding = 0
            self.app.spotify_link = self.query_one("#search-input").value
            self.app.query_one("#interface").loading = True
            self.app.query_one("#exit-button").disabled = True
            self.query_one("#search-input").visible = False
            self.query_one("#app-description").visible = False
            self.query_one("#search-button").visible = False
            self.get_link_info()

    def on_input_changed(self, event: Input.Changed):
        if input_validator(event.input.value):
            self.app.query_one("#search-input", Input).styles.border = ("tall", "green")
            self.app.query_one("#search-button").disabled = False
        elif event.input.value == "":
            self.app.query_one("#search-input", Input).styles.border = ("tall", "black")
        else:
            self.app.query_one("#search-input", Input).styles.border = ("tall", "red")
            self.app.query_one("#search-button").disabled = True

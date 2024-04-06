from textual.widgets import Input, Button, Label
from textual.screen import Screen
from textual.containers import Horizontal

from spotidex.cli.custom_widgets.AppInterface import AppInterface
from spotidex.cli.app_screens.MainMenuInterface import MainMenuInterface
from spotidex.cli.utils import input_validator,app_description
from spotidex.cli.utils import get_link_details

from textual.worker import Worker, get_current_worker
from textual import work

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
    border: round ansi_bright_cyan;
    border-title-align: center;

}

#search-input:blur{
    border:tall black
}
"""

class Search(Screen):
    DEFAULT_CSS = CSS
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
    
    @work(exclusive=True, thread=True)
    def get_link_info(self):
        self.app.query_one("LoadingIndicator").styles.background = "#1c1c1c"
        try:
            self.app.link_details = get_link_details(self.app.spotify_link)
        except Exception:
            get_current_worker().cancel()
        self.app.query_one("#interface").loading = False
        self.app.query_one("#exit-button").disabled = False
        self.app.query_one("#interface").styles.padding = (2,3,0,3)
        
        
    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if str(event.state) == "WorkerState.CANCELLED":
            self.app.notify("Network Connection Error",title="SPOTIDEX",severity="error")
            self.query_one('#search-input').visible = True
            self.query_one('#app-description').visible = True
            self.query_one('#search-button').visible = True
        elif str(event.state) == "WorkerState.SUCCESS":
            self.app.push_screen(MainMenuInterface())
            self.query_one('#search-input').visible = True
            self.query_one('#app-description').visible = True
            self.query_one('#search-button').visible = True
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
            self.query_one('#search-input').visible = False
            self.query_one('#app-description').visible = False
            self.query_one('#search-button').visible = False
            self.get_link_info()
        
    def on_input_changed(self, event: Input.Changed):
        if input_validator(event.input.value):
            self.app.query_one("#search-input",Input).styles.border = ("tall","green")
            self.app.query_one("#search-button").disabled = False
        elif event.input.value == "":
            self.app.query_one("#search-input",Input).styles.border = ("tall","black")
        else:
            self.app.query_one("#search-input",Input).styles.border = ("tall","red")
            self.app.query_one("#search-button").disabled = True

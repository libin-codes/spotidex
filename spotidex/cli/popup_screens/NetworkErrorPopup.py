from textual.screen import ModalScreen
from textual.widgets import Label,Button
from textual.containers import Grid

CSS ='''

NetworkErrorScreen {
    align: center middle;
}

#network-error-dialog-box{
    grid-size: 2 3;
    grid-gutter: 1 2;
    grid-rows: 1fr 2fr 3;
    padding: 0 1;
    width: 50;
    height: 11;
    border: thick $background 80%;
    background: $surface;
}

#error-label {
    column-span: 2;
    height: 1fr;
    width: 2fr;
    content-align: center middle;
}

#error-heading {
    column-span: 2;
    height: 1fr;
    width: 1fr;
    content-align: center middle;
    color:$primary
}

#retry-button {
    width: 100%;
    column-span: 1;
}

#exit-button {
    width: 100%;
    column-span: 1;
}

'''

class NetworkErrorScreen(ModalScreen):
    DEFAULT_CSS = CSS
    def compose(self):
        yield Grid(
            Label("[bold]NETWORK ERROR",id="error-heading"),
            Label("CHECK YOUR INTERNET CONNECTION", id="error-label"),
            Button("RETRY", id="retry-button",variant='warning'),
            Button("EXIT", variant="error", id="exit-button"),
            id="network-error-dialog-box",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit-button":
            self.app.exit()
        else:
            self.dismiss("retry")
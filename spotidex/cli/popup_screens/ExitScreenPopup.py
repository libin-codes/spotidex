from textual.screen import ModalScreen
from textual.widgets import Label,Button
from textual.containers import Grid

CSS ='''

ExitScreen {
    align: center middle;
}

#exit-dialog-box{
    grid-size: 2;
    grid-gutter: 1 2;
    grid-rows: 1fr 3;
    padding: 0 1;
    width: 50;
    height: 11;
    border: thick $background 80%;
    background: $surface;
}

#exit-question {
    column-span: 2;
    height: 1fr;
    width: 1fr;
    content-align: center middle;
}

#yes-exit-button {
    width: 100%;
}

#exit-no-button {
    width: 100%;
}

'''

class ExitScreen(ModalScreen):
    DEFAULT_CSS = CSS
    def compose(self):
        yield Grid(
            Label("[bold]ARE YOU SURE YOU WANT TO EXIT?", id="exit-question"),
            Button("YES", id="yes-exit-button",variant='success'),
            Button("NO", variant="error", id="exit-no-button"),
            id="exit-dialog-box",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes-exit-button":
            exit()
        else:
            self.dismiss()
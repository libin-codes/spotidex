from textual.screen import ModalScreen
from textual.widgets import Label,Button
from textual.containers import Grid

CSS ='''

GoBackSettings {
    align: center middle;
}

#goback-dialog-box{
    grid-size: 2;
    grid-gutter: 1 2;
    grid-rows: 1fr 3;
    padding: 0 1;
    width: 50;
    height: 11;
    border: thick $background 80%;
    background: $surface;
}

#goback-question {
    column-span: 2;
    height: 1fr;
    width: 1fr;
    content-align: center middle;
}

#save-changes-button {
    width: 100%;
}

#dont-save-changes-button {
    width: 100%;
}

'''

class GoBackSettings(ModalScreen):
    DEFAULT_CSS = CSS
    def compose(self):
        yield Grid(
            Label("[bold]DO YOU WANT TO SAVE YOUR CHANGES?", id="goback-question"),
            Button("SAVE CHANGES", id="save-changes-button",variant='success'),
            Button("DONT SAVE", variant="error", id="dont-save-changes-button"),
            id="goback-dialog-box",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-changes-button":
            self.dismiss(True)
        else:
            self.dismiss(False)
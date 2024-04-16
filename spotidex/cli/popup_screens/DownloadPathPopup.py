from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, RichLog, Button
from textual.containers import Container

from spotidex.cli.utils import (
    shorten_path,
    Path,
    get_data_drive_path,
    get_downloads_folder,
    os,
    can_create_directory,
)

CSS = """
DownloadPathScreen{
  
    align:center middle;

}
DirectoryTree{
    background:transparent;
}

#downloadpath-main-container{
    padding: 0 1;
    width: 75;
    height: 22;
    border: thick $background 80%;
    background: $surface;

}

#select-download-path-container{
    width:71;
    height:13;
    background:$boost;
    padding:1;

}

#download-path-log{
    background:transparent;
    width:75;
}

#download-path-log-container{
    padding-left:2;
    width:63;
    height:3;
    border:grey;
}

#download-path-button-container{
    layout:horizontal;
    height:3;
    width:71;
    margin-top:1;
    align:center middle;
}

#download-path-confirm-button{
    width:23;
    dock:right;

}

#download-path-reset-button{
    width:22;
    
}

#download-path-back-button{
    
    height:3;
    width:4;
    min-width:8;
    dock:right;
    border:gray;
    background:transparent;

}

#downloads-folder-button{
    width:22;
    dock:left;
}

#download-path-back-button:hover {
   tint: $background 20%;
}

"""


class DownloadPathScreen(ModalScreen):
    DEFAULT_CSS = CSS
    current_path = str(Path(get_data_drive_path()))

    class FilteredDirectoryTree(DirectoryTree):
        def filter_paths(self, paths):
            self.show_root = False
            self.show_guides = False
            self.guide_depth = 3
            return [path for path in paths if path.is_dir()]

    def compose(self):
        with Container(id="downloadpath-main-container"):
            with Container(id="download-path-log-container"):
                yield RichLog(
                    highlight=True, markup=True, id="download-path-log"
                ).write(shorten_path(self.current_path, 60))
            yield Button("BACK", id="download-path-back-button", variant="primary")
            with Container(id="select-download-path-container"):
                yield self.FilteredDirectoryTree(self.current_path, id="filteredtree")
            with Container(id="download-path-button-container"):
                yield Button(
                    "DOWNLOADS FOLDER", id="downloads-folder-button", variant="warning"
                )
                yield Button(
                    "CURRENT DIRECTORY",
                    id="download-path-reset-button",
                    variant="error",
                )
                yield Button(
                    "CONFIRM", id="download-path-confirm-button", variant="success"
                )

    def refresh_tree(self):
        self.app.query_one("#select-download-path-container").remove_children()
        self.app.query_one("#select-download-path-container").mount(
            self.FilteredDirectoryTree(self.current_path, id="filteredtree")
        )
        self.app.query_one("#download-path-log").clear().write(
            shorten_path(self.current_path, 60)
        )

    def on_directory_tree_directory_selected(self, path):
        self.current_path = str(path.path)
        self.refresh_tree()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download-path-back-button":
            if os.name == "nt":
                self.current_path = str(
                    Path("\\".join(self.current_path.split("\\")[:-1]) + "\\")
                )
            else:
                self.current_path = str(
                    Path("/".join(self.current_path.split("/")[:-1]) + "/")
                )
            self.refresh_tree()

        elif event.button.id == "download-path-reset-button":
            self.current_path = str(Path.cwd())
            self.refresh_tree()

        elif event.button.id == "downloads-folder-button":
            self.current_path = str(get_downloads_folder())
            self.refresh_tree()

        elif event.button.id == "download-path-confirm-button":
            if can_create_directory(self.current_path):
                self.dismiss(self.current_path)
            else:
                self.app.notify(
                    "Cannot access the given path, please run the terminal as administrator or use other path",
                    title="PERMISSION DENIED",severity="warning"
                )

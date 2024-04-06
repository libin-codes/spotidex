from textual.app import App
from spotidex.cli.app_screens.SearchInterface import Search
from spotidex.cli.app_screens.SettingsInterface import Settings
from spotidex.cli.utils import Path


class SpotidexApp(App):
    TITLE = "SPOTIDEX"
    SUB_TITLE = "SPOTIFY DOWNLOADER"
    SCREENS = {"SettingsScreen": Settings}

    def on_ready(self) -> None:
        self.app.saved_settings = {
            "add_metadata": True,
            "download_path": str(Path.cwd()),
            "download_quality": "high",
        }
        self.push_screen(Search())
 
def main():
    SpotidexApp().run()




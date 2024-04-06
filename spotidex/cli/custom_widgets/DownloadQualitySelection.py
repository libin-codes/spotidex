from textual.widgets import Label, Select
from textual.containers import Container
from textual.widget import Widget
from textual.reactive import reactive
from textual import on

CSS = """
DownloadQualitySelection{
    height:auto;
    width:auto;
}

#download-quality-container{
    layout:horizontal;
    width:55;
    height:5;
    background:$boost;}

#download-quality-selection{
    width: 33;
    margin-left:1;
    margin-top:1;}

#download-quality-label{
    background:$boost;
    height:5;
    content-align:center middle;
    padding:1;}

#download-quality-selection > SelectCurrent {
    border: tall $boost;}
"""


class DownloadQualitySelection(Widget):
    DEFAULT_CSS = CSS
    value = reactive("high")
    def compose(self):
        options = [
            ("LOW QUALITY    [24  kbps]","low"),
            ("MEDIUM QUALITY [128 kbps]","medium"),
            ("HIGH QUALITY   [320 kbps]","high"),
        ]
        with Container(id="download-quality-container"):
            yield Label(" DOWNLOAD QUALITY ", id="download-quality-label")
            yield Select(
                options,
                allow_blank=False,
                id="download-quality-selection",
                
            )
    def on_select_changed(self):
        self.value = self.query_one(Select).value
    def watch_value(self,value):
        self.query_one(Select).value = value

import sys

sys.path.append("D:/Coding Projects/gui")
from textual.app import App


class TestApp(App):
    TITLE = "TEST APP"

    def compose(self):
        yield DownloadQualitySelection()

if __name__ == "__main__":
    TestApp().run()

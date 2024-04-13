from textual.containers import Container
from textual.widgets import Static
from textual.widget import Widget
from textual.reactive import reactive

CSS = """
MetadataCheckBox{
    height:auto;
    width:auto;

}

#main-container{
    height:auto;
    width:auto;
    padding: 1 2;
    background:$boost;
}


#metadata-checkbox-container{
    layout:horizontal;
    width:auto;
    height:3;
    background:$boost;
}

#metadata-checkbox-label{
    width:auto;
    margin-top:1;
    margin-left:2;
}

#metadata-checkbox{
    border:thick transparent ;
    width:7;
    height:3;
    dock:right;
    padding-left:1;
    margin-left:1;
  
}

#metadata-checkbox:hover{
    opacity:0.8;

}


.inactive{
    background:$error 8%;
}
.active{
    background:$success 8%;
}

"""


class MetadataCheckBox(Widget):
    DEFAULT_CSS = CSS
    SCOPED_CSS = True
    value = reactive(True)

    def compose(self):
        with Container(id="main-container"):
            with Container(id="metadata-checkbox-container"):
                yield Static("INCLUDE METADATA", id="metadata-checkbox-label")
                yield Static(id="metadata-checkbox")

    def watch_value(self, value):
        if value == True:
            self.query_one("#metadata-checkbox").update("🟢")
            self.query_one("#metadata-checkbox").remove_class("inactive")
            self.query_one("#metadata-checkbox").add_class("active")
        else:
            self.query_one("#metadata-checkbox").update("🔴")
            self.query_one("#metadata-checkbox").remove_class("active")
            self.query_one("#metadata-checkbox").add_class("inactive")
 

    def on_click(self) -> None:
        if self.value == True:
            self.value = False
        else:
            self.value = True

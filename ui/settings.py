from textual.widgets import Select, Static, Label, Button
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from core.tools import ToolSuite

class SettingsModal(ModalScreen):
    """
    A modal for changing global settings like the wireless interface.
    """
    CSS = """
    SettingsModal {
        align: center middle;
    }
    #settings_dialog {
        padding: 1 2;
        border: solid blue;
        width: 60;
        height: auto;
        background: $surface;
    }
    """

    def compose(self):
        tools = ToolSuite()
        interfaces = tools.list_interfaces()
        options = [(iface, iface) for iface in interfaces]
        
        with Vertical(id="settings_dialog"):
            yield Label("[bold]VALKYRIE SETTINGS[/bold]")
            yield Label("Select Wireless Interface:")
            yield Select(options, id="select_interface", prompt="Choose Adapter...")
            
            with Horizontal():
                yield Button("Apply", variant="primary", id="save")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            iface = self.query_one("#select_interface").value
            self.dismiss(iface)
        else:
            self.dismiss(None)

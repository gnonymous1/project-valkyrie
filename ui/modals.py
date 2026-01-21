from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button
from textual.containers import Vertical, Horizontal

class APIKeyModal(ModalScreen):
    CSS = """
    APIKeyModal {
        align: center middle;
    }
    #dialog {
        padding: 1 2;
        border: solid green;
        width: 60;
        height: auto;
        background: $surface;
    }
    Input {
        margin: 1 0;
    }
    #buttons {
        align: right middle;
    }
    """

    def compose(self):
        with Vertical(id="dialog"):
            yield Label("Enter Gemini API Key:")
            yield Input(placeholder="AI Studio Key...", password=True, id="key_input")
            with Horizontal(id="buttons"):
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", variant="error", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            key = self.query_one("#key_input").value
            self.dismiss(key)
        else:
            self.dismiss(None)

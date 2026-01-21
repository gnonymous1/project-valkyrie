from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button
from textual.containers import Vertical, Horizontal
from core.ai import GeminiClient
import threading

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
            yield Label("[bold]GEMINI AI CONFIGURATION[/bold]")
            yield Label("Enter Gemini API Key:")
            yield Input(placeholder="AI Studio Key...", password=True, id="key_input")
            yield Label("", id="status_msg")
            with Horizontal(id="buttons"):
                yield Button("Test", variant="warning", id="test")
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", variant="error", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        key = self.query_one("#key_input").value
        msg = self.query_one("#status_msg")
        
        if event.button.id == "test":
            if not key:
                msg.update("[red]Enter a key first![/red]")
                return
            
            msg.update("[yellow]Testing...[/yellow]")
            def check():
                client = GeminiClient()
                if client.validate_key(key):
                    # Use app.call_from_thread to update UI safely
                    self.app.call_from_thread(msg.update, "[green]Connection Successful![/green]")
                else:
                    self.app.call_from_thread(msg.update, "[red]Invalid Key or No Connection[/red]")
            
            threading.Thread(target=check, daemon=True).start()

        elif event.button.id == "save":
            self.dismiss(key)
        else:
            self.dismiss(None)

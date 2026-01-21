from textual.widgets import Static, Button, Label
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from core.knowledge_base import NetworkTarget
import logging

class TargetControlPanel(Static):
    """
    A panel for controlling actions on the selected Wi-Fi target.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_target = None
        self.logger = logging.getLogger(__name__)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("[bold]TARGET CONTROL CENTER[/bold]", id="panel_title")
            yield Label("No Target Selected", id="target_info")
            
            with Vertical(id="action_buttons"):
                yield Button("AI ANALYSIS", variant="primary", id="btn_ai", disabled=True)
                yield Button("WPS ATTACK", variant="warning", id="btn_wps", disabled=True)
                yield Button("CAPTURE PMKID", variant="warning", id="btn_pmkid", disabled=True)
                yield Button("DEAUTH & HANDSHAKE", variant="error", id="btn_deauth", disabled=True)
            
            yield Label("\n[bold]GLOBAL CONTROLS[/bold]")
            with Horizontal():
                yield Button("START SCAN", variant="success", id="btn_scan")
                yield Button("STOP SCAN", variant="error", id="btn_stop")
                
            # Status display for user feedback
            yield Label("", id="status_message")

    def update_target(self, target: NetworkTarget):
        self.selected_target = target
        info = self.query_one("#target_info")
        
        if target:
            info.update(f"[cyan]Target:[/cyan] {target.ssid}\n[cyan]BSSID:[/cyan] {target.bssid}\n[cyan]Signal:[/cyan] {target.signal_strength}dBm")
            
            # Enable buttons based on capabilities
            self.query_one("#btn_ai").disabled = False
            self.query_one("#btn_wps").disabled = not target.wps_enabled
            self.query_one("#btn_pmkid").disabled = False
            self.query_one("#btn_deauth").disabled = False
        else:
            info.update("No Target Selected")
            for btn in self.query_all("Button"):
                if "btn_scan" not in btn.id and "btn_stop" not in btn.id:
                    btn.disabled = True
    
    def update_status(self, message: str, status_type: str = "info"):
        """Update the status message with color coding"""
        status_label = self.query_one("#status_message")
        color_map = {
            "info": "[blue]",
            "success": "[green]",
            "warning": "[yellow]",
            "error": "[red]"
        }
        color = color_map.get(status_type, "[blue]")
        status_label.update(f"{color}{message}[/]")
        self.logger.info(f"Status: {message}")
    
    def clear_status(self):
        """Clear the status message"""
        status_label = self.query_one("#status_message")
        status_label.update("")

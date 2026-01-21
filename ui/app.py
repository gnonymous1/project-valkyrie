from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Label, DataTable
from ui.widgets import NetworkTable, AgentLog, StatusHeader
from core.knowledge_base import KnowledgeBase
from core.ai import GeminiClient
from core.tools import ToolSuite
from ui.modals import APIKeyModal
from ui.control_panel import TargetControlPanel
from ui.settings import SettingsModal
import threading
import time

# Import Agents
from agents.ethics import EthicsAgent
from agents.environment import EnvironmentAgent
from agents.recon import ReconAgent
from agents.threat import ThreatModelingAgent
from agents.evasion import DefenseEvasionAgent
from agents.exploitation import ExploitationAgent
from agents.recovery import FailureRecoveryAgent

class WifiAgentApp(App):
    TITLE = "PROJECT VALKYRIE: Autonomous Wireless Interdiction Swarm"
    CSS = """
    Screen {
        layout: vertical;
    }
    .box {
        height: 100%;
        border: solid green;
        padding: 1;
    }
    #top-row {
        height: 70%;
    }
    #bottom-row {
        height: 30%;
        border: solid yellow;
        padding: 1;
    }
    #left-pane {
        width: 60%;
    }
    #right-pane {
        width: 40%;
    }
    #action_buttons Button {
        width: 100%;
        margin-bottom: 1;
    }
    APIKeyModal, SettingsModal {
        align: center middle;
    }
    """
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dry_run", "Toggle Dry Run"),
        ("s", "open_settings", "Settings"),
        ("k", "configure_api_key", "AI Key")
    ]

    def __init__(self, dry_run=False, interface="wlan0"):
        super().__init__()
        self.kb = KnowledgeBase()
        self.kb.environment.dry_run = dry_run
        self.kb.environment.managed_interface = interface
        self.kb.environment.mon_interface = f"{interface}mon" if dry_run else None
        
        self.ai = GeminiClient()
        self.tools = ToolSuite()
        self.scanning = True
        self.running = True
        self.agent_thread = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield StatusHeader(id="status_header")
        
        with Horizontal(id="top-row"):
            with Vertical(id="left-pane", classes="box"):
                yield Label("[reverse] DISCOVERED TARGETS [/reverse]")
                yield NetworkTable(id="network_table")
                
            with Vertical(id="right-pane", classes="box"):
                yield TargetControlPanel(id="control_panel")
        
        with Vertical(id="bottom-row"):
            yield Label("[reverse] AGENT ACTIVITY LOG [/reverse]")
            yield AgentLog(id="agent_log")
        
        yield Footer()

    def on_mount(self) -> None:
        if not self.ai.api_key:
            self.push_screen(APIKeyModal(), self.set_api_key)

        self.agent_thread = threading.Thread(target=self.run_agent_swarm, daemon=True)
        self.agent_thread.start()
        self.set_interval(1.0, self.update_ui)

    def set_api_key(self, key: str | None) -> None:
        if key:
            if self.ai.configure(key):
                self.notify("API Key Configured Successfully!")
            else:
                self.notify("Failed to configure API Key.", severity="error")

    def action_configure_api_key(self) -> None:
        self.push_screen(APIKeyModal(), self.set_api_key)

    def action_open_settings(self) -> None:
        self.push_screen(SettingsModal(), self.set_interface)

    def set_interface(self, iface: str | None) -> None:
        if iface:
            self.kb.environment.managed_interface = iface
            self.notify(f"Interface changed to {iface}")
            self.kb.environment.mon_interface = None # Force re-init

    def update_ui(self) -> None:
        table = self.query_one("#network_table")
        table.update_data()
        self.query_one("#agent_log").update_log()
        
        # Update Control Panel with selected target
        try:
            # coordinate_to_cell_key might return None if no selection
            coord = table.cursor_coordinate
            row_key = table.coordinate_to_cell_key(coord).row_key
            if row_key:
                target_bssid = str(row_key.value)
                target = self.kb.get_target(target_bssid)
                self.query_one("#control_panel").update_target(target)
        except Exception:
            pass

        status = "Scanning" if self.scanning else "Idle"
        iface = self.kb.environment.mon_interface or self.kb.environment.managed_interface
        self.query_one("#status_header").update_status(status, iface)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        target = self.query_one("#control_panel").selected_target
        mon_iface = self.kb.environment.mon_interface or self.kb.environment.managed_interface

        if event.button.id == "btn_scan":
            self.scanning = True
            self.notify("Manual scanning started.")
        elif event.button.id == "btn_stop":
            self.scanning = False
            self.notify("Scanning paused.")
        elif event.button.id == "btn_ai" and target:
            self.notify(f"AI Analyzing {target.ssid}...")
            threading.Thread(target=self.ai_analyze, args=(target,), daemon=True).start()
        elif event.button.id == "btn_deauth" and target:
            self.notify(f"Deauth Attack on {target.ssid}...")
            threading.Thread(target=self.tools.capture_handshake, args=(mon_iface, target), daemon=True).start()
        elif event.button.id == "btn_pmkid" and target:
            self.notify(f"PMKID Capture on {target.ssid}...")
            threading.Thread(target=self.tools.capture_pmkid, args=(mon_iface, target), daemon=True).start()
        elif event.button.id == "btn_wps" and target:
            self.notify(f"WPS Attack on {target.ssid}...")
            threading.Thread(target=self.tools.attack_wps, args=(mon_iface, target), daemon=True).start()

    def ai_analyze(self, target):
        analysis = self.ai.analyze_target(target.ssid, target.encryption)
        self.kb.log_action("GEMINI_AI", f"Result for {target.ssid}", analysis)

    def run_agent_swarm(self):
        agents = {
            "ethics": EthicsAgent(),
            "recovery": FailureRecoveryAgent(),
            "environment": EnvironmentAgent(),
            "evasion": DefenseEvasionAgent(),
            "recon": ReconAgent(),
            "threat": ThreatModelingAgent(),
            "exploit": ExploitationAgent(),
        }
        
        while self.running:
            if not self.scanning:
                time.sleep(1)
                continue

            # Standard agent loop
            try:
                agents["recovery"].run()
                agents["environment"].run()
                agents["ethics"].run()
                agents["evasion"].run()
                agents["recon"].run()
                agents["threat"].run()
                agents["exploit"].run()
            except Exception as e:
                self.kb.log_action("SYSTEM", "Error in swarm", str(e))
            
            time.sleep(5)

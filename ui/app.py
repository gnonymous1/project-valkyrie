from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Label
from ui.widgets import NetworkTable, AgentLog, StatusHeader
from core.knowledge_base import KnowledgeBase
from core.ai import GeminiClient
import threading
import time
import asyncio

# Import Agents
from agents.ethics import EthicsAgent
from agents.environment import EnvironmentAgent
from agents.recon import ReconAgent
from agents.threat import ThreatModelingAgent
from agents.evasion import DefenseEvasionAgent
from agents.exploitation import ExploitationAgent
from agents.recovery import FailureRecoveryAgent
from agents.reporting import ReportingAgent

class WifiAgentApp(App):
    TITLE = "PROJECT VALKYRIE: Autonomous Wireless Interdiction Swarm"
    CSS = """
    Screen {
        layout: vertical;
    }
    .box {
        height: 100%;
        border: solid green;
    }
    #left-pane {
        width: 50%;
    }
    #right-pane {
        width: 50%;
    }
    """
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dry_run", "Toggle Dry Run"),
        ("a", "analyze_target", "AI Analyze Selected")
    ]

    def __init__(self, dry_run=False, interface="wlan0"):
        super().__init__()
        self.kb = KnowledgeBase()
        self.kb.environment.dry_run = dry_run
        self.kb.environment.managed_interface = interface
        self.kb.environment.mon_interface = f"{interface}mon" if dry_run else None
        
        self.ai = GeminiClient()
        self.running = True
        self.agent_thread = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield StatusHeader(id="status_header")
        
        with Horizontal():
            with Vertical(id="left-pane", classes="box"):
                yield Label("Discovered Targets (Live)")
                yield NetworkTable(id="network_table")
                
            with Vertical(id="right-pane", classes="box"):
                yield Label("Agent Activity Log")
                yield AgentLog(id="agent_log")
        
        yield Footer()

    def on_mount(self) -> None:
        # Start Agent Swarm in Background Thread
        self.agent_thread = threading.Thread(target=self.run_agent_swarm, daemon=True)
        self.agent_thread.start()
        
        # Start UI Update Timer
        self.set_interval(1.0, self.update_ui)

    def update_ui(self) -> None:
        self.query_one("#network_table").update_data()
        self.query_one("#agent_log").update_log()
        
        status = "Active" if self.running else "Stopped"
        iface = self.kb.environment.mon_interface or "Initializing..."
        self.query_one("#status_header").update_status(status, iface)

    def action_analyze_target(self) -> None:
        table = self.query_one("#network_table")
        try:
            # Get selected row key (BSSID)
            # Textual DataTable APIs can be tricky, assuming simplest selection
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
            if not row_key: return
            
            target = self.kb.get_target(str(row_key.value))
            if target:
                self.notify(f"Asking Gemini about {target.ssid}...")
                
                # Run AI in thread to avoid blocking UI
                def ask_ai():
                    analysis = self.ai.analyze_target(target.ssid, target.encryption)
                    self.kb.log_action("GEMINI_AI", "Analysis", "Completed")
                    # In a real app we'd show a modal, here we log it
                    self.kb.log_action("GEMINI_AI_RESULT", "Response", analysis)
                
                threading.Thread(target=ask_ai, daemon=True).start()
                
        except Exception as e:
            self.notify("Select a target first!")

    def run_agent_swarm(self):
        """
        The main agent loop, running in a background thread.
        """
        agents = {
            "ethics": EthicsAgent(),
            "recovery": FailureRecoveryAgent(),
            "environment": EnvironmentAgent(),
            "evasion": DefenseEvasionAgent(),
            "recon": ReconAgent(),
            "threat": ThreatModelingAgent(),
            "exploit": ExploitationAgent(),
            # ReportingAgent is disabled in UI mode logs handle it
        }
        
        loop_count = 1
        while self.running:
            # 1. Recovery
            if not agents["recovery"].run(): break
            
            # 2. Env/Ethics
            agents["environment"].run()
            agents["ethics"].run()
            
            # 3. Action
            agents["evasion"].run()
            agents["recon"].run()
            agents["threat"].run()
            agents["exploit"].run()
            
            time.sleep(5)
            loop_count += 1

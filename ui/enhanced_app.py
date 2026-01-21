from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Button, Label, DataTable, Input, Checkbox, TabbedContent, TabPane
from textual.screen import ModalScreen
from ui.widgets import NetworkTable, AgentLog, StatusHeader
from core.knowledge_base import KnowledgeBase
from core.ai import GeminiClient
from core.tools import ToolSuite
from ui.modals import APIKeyModal
from ui.settings import SettingsModal
import threading
import time
import logging
import subprocess
import psutil

# Import Agents
from agents.ethics import EthicsAgent
from agents.environment import EnvironmentAgent
from agents.recon import ReconAgent
from agents.threat import ThreatModelingAgent
from agents.evasion import DefenseEvasionAgent
from agents.exploitation import ExploitationAgent
from agents.recovery import FailureRecoveryAgent


class NetworkConfigModal(ModalScreen):
    """Modal for network configuration settings"""
    CSS = """
    NetworkConfigModal {
        align: center middle;
    }
    #network_dialog {
        padding: 1 2;
        border: solid blue;
        width: 70;
        height: auto;
        background: $surface;
    }
    Input {
        margin: 1 0;
    }
    """

    def __init__(self, kb):
        super().__init__()
        self.kb = kb

    def compose(self):
        with Vertical(id="network_dialog"):
            yield Label("[bold]NETWORK CONFIGURATION[/bold]")
            
            # Monitor mode toggle
            yield Label("Monitor Mode:")
            yield Checkbox("Enable Monitor Mode", id="monitor_mode", value=False)
            
            # Channel selection
            yield Label("Channel (1-11):")
            yield Input(placeholder="Channel (default: auto)", id="channel_input")
            
            # Airgeddon twin attack settings
            yield Label("Airgeddon Twin Attack Settings:")
            yield Checkbox("Enable Twin Attack", id="twin_attack", value=False)
            yield Input(placeholder="Target BSSID for twin attack", id="twin_bssid")
            
            # Deauth settings
            yield Label("Deauthentication Settings:")
            yield Input(placeholder="Number of deauth packets (default: 10)", id="deauth_count")
            
            # Network reset options
            yield Label("Network Reset Options:")
            yield Checkbox("Reset Interface", id="reset_interface", value=False)
            yield Checkbox("Restart Network Manager", id="restart_nm", value=False)
            
            with Horizontal():
                yield Button("Apply", variant="primary", id="apply")
                yield Button("Test Connection", variant="warning", id="test_conn")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        tools = ToolSuite()
        
        if event.button.id == "test_conn":
            # Test network connectivity
            try:
                result = subprocess.run(['ping', '-c', '1', 'google.com'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.app.notify("Network connectivity: OK", severity="success")
                else:
                    self.app.notify("Network connectivity: FAILED", severity="error")
            except subprocess.TimeoutExpired:
                self.app.notify("Network connectivity: TIMEOUT", severity="error")
            except Exception as e:
                self.app.notify(f"Network test error: {e}", severity="error")
                
        elif event.button.id == "apply":
            # Apply network settings
            try:
                # Get values from inputs
                monitor_enabled = self.query_one("#monitor_mode").value
                channel = self.query_one("#channel_input").value or None
                twin_attack = self.query_one("#twin_attack").value
                twin_bssid = self.query_one("#twin_bssid").value if twin_attack else None
                deauth_count = self.query_one("#deauth_count").value or "10"
                
                # Apply monitor mode if requested
                if monitor_enabled and hasattr(self.kb.environment, 'managed_interface'):
                    interface = self.kb.environment.managed_interface
                    mon_interface = tools.enable_monitor_mode(interface)
                    if mon_interface:
                        self.kb.environment.mon_interface = mon_interface
                        self.app.notify(f"Monitor mode enabled on {mon_interface}", severity="success")
                    else:
                        self.app.notify("Failed to enable monitor mode", severity="error")
                
                # Store twin attack settings
                if twin_bssid:
                    self.kb.twin_attack_enabled = twin_attack
                    self.kb.twin_attack_target = twin_bssid
                
                # Store deauth settings
                try:
                    self.kb.deauth_count = int(deauth_count)
                except ValueError:
                    self.kb.deauth_count = 10
                
                self.app.notify("Network settings applied", severity="success")
                self.dismiss(True)
            except Exception as e:
                self.app.notify(f"Error applying settings: {e}", severity="error")
        else:
            self.dismiss(False)


class AIAssessmentModal(ModalScreen):
    """Modal for AI-powered network assessment"""
    CSS = """
    AIAssessmentModal {
        align: center middle;
    }
    #ai_dialog {
        padding: 1 2;
        border: solid green;
        width: 80;
        height: 70%;
        background: $surface;
    }
    """

    def __init__(self, kb, ai_client):
        super().__init__()
        self.kb = kb
        self.ai = ai_client

    def compose(self):
        with Vertical(id="ai_dialog"):
            yield Label("[bold]AI NETWORK ASSESSMENT[/bold]")
            yield Label("This will perform an automated AI analysis of all discovered networks.")
            yield Label("Warning: This may take several minutes depending on the number of targets.")
            
            # Assessment options
            yield Checkbox("Analyze all targets", id="analyze_all", value=True)
            yield Checkbox("Generate comprehensive report", id="generate_report", value=True)
            yield Checkbox("Suggest attack vectors", id="suggest_attacks", value=True)
            
            # Progress indicator
            yield Label("", id="progress_label")
            
            # Results display
            yield Label("[bold]AI Assessment Results:[/bold]")
            with ScrollableContainer(height="40%"):
                yield Label("", id="results_display")
            
            with Horizontal():
                yield Button("Start Assessment", variant="primary", id="start_assessment")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start_assessment":
            # Start AI assessment in a separate thread
            threading.Thread(target=self._perform_assessment, daemon=True).start()
        else:
            self.dismiss()

    def _perform_assessment(self):
        try:
            targets = self.kb.targets
            results = []
            
            for i, (bssid, target) in enumerate(targets.items()):
                self.app.call_from_thread(
                    self.query_one("#progress_label").update,
                    f"Analyzing {target.ssid} ({i+1}/{len(targets)})..."
                )
                
                # Perform AI analysis
                analysis = self.ai.analyze_target(
                    target.ssid, 
                    target.encryption,
                    target.vendor if hasattr(target, 'vendor') else "Unknown"
                )
                
                results.append(f"[b]{target.ssid}[/b] ({target.bssid}):\n{analysis}\n")
                
                # Update results display
                self.app.call_from_thread(
                    self.query_one("#results_display").update,
                    "\n".join(results)
                )
                
                # Small delay to allow UI updates
                time.sleep(0.5)
            
            self.app.call_from_thread(
                self.query_one("#progress_label").update,
                "Assessment complete!"
            )
            
        except Exception as e:
            self.app.call_from_thread(
                self.query_one("#progress_label").update,
                f"Assessment error: {e}"
            )


class EnhancedWifiAgentApp(App):
    TITLE = "PROJECT VALKYRIE: Advanced Wireless Interdiction System"
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
        height: 60%;
    }
    #middle-row {
        height: 25%;
        border: solid yellow;
        padding: 1;
    }
    #bottom-row {
        height: 15%;
        border: solid red;
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
    #global_controls Button {
        width: 48%;
        margin-right: 2%;
    }
    APIKeyModal, SettingsModal, NetworkConfigModal, AIAssessmentModal {
        align: center middle;
    }
    .status_connected {
        color: green;
    }
    .status_disconnected {
        color: red;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dry_run", "Toggle Dry Run"),
        ("s", "open_settings", "Settings"),
        ("n", "open_network_config", "Network Config"),
        ("a", "open_ai_assessment", "AI Assessment"),
        ("k", "configure_api_key", "AI Key"),
        ("ctrl+r", "refresh_display", "Refresh Display"),
        ("space", "toggle_scanning", "Toggle Scan")
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
        self.logger = logging.getLogger(__name__)
        
        # Track AI connection status
        self.ai_connected = False
        self.ai_test_thread = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield StatusHeader(id="status_header")
        
        with Horizontal(id="top-row"):
            with Vertical(id="left-pane", classes="box"):
                yield Label("[reverse] DISCOVERED TARGETS [/reverse]")
                yield NetworkTable(id="network_table")
                
            with Vertical(id="right-pane", classes="box"):
                yield Label("[reverse] TARGET CONTROL CENTER [/reverse]")
                with TabbedContent():
                    with TabPane("Single Target"):
                        yield Label("Selected Target Details", id="target_info")
                        with Vertical(id="action_buttons"):
                            yield Button("AI ANALYSIS", variant="primary", id="btn_ai", disabled=True)
                            yield Button("WPS ATTACK", variant="warning", id="btn_wps", disabled=True)
                            yield Button("CAPTURE PMKID", variant="warning", id="btn_pmkid", disabled=True)
                            yield Button("DEAUTH & HANDSHAKE", variant="error", id="btn_deauth", disabled=True)
                    
                    with TabPane("Batch Operations"):
                        yield Button("AI ANALYZE ALL", variant="primary", id="btn_ai_all")
                        yield Button("ATTACK ALL WPS", variant="warning", id="btn_wps_all")
                        yield Button("DEAUTH ALL", variant="error", id="btn_deauth_all")
        
        with Vertical(id="middle-row"):
            yield Label("[reverse] GLOBAL CONTROLS [/reverse]")
            with Horizontal(id="global_controls"):
                yield Button("START SCAN", variant="success", id="btn_scan")
                yield Button("STOP SCAN", variant="error", id="btn_stop")
                yield Button("AIRGEDDON TWIN ATTACK", variant="warning", id="btn_twin_attack")
                yield Button("NETWORK RESET", variant="error", id="btn_net_reset")
            
            # Status indicators
            with Horizontal():
                yield Label("AI Connection:", id="ai_status_label")
                yield Label("[red]DISCONNECTED[/red]", id="ai_connection_status")
                yield Button("TEST AI", variant="warning", id="btn_test_ai")
                yield Button("AI ASSESSMENT", variant="primary", id="btn_ai_assessment")
        
        with Vertical(id="bottom-row"):
            yield Label("[reverse] AGENT ACTIVITY LOG [/reverse]")
            yield AgentLog(id="agent_log")
        
        yield Footer()

    def on_mount(self) -> None:
        if not self.ai.api_key:
            self.push_screen(APIKeyModal(), self.set_api_key)

        # Start agent swarm
        self.agent_thread = threading.Thread(target=self.run_agent_swarm, daemon=True)
        self.agent_thread.start()
        
        # Start periodic updates
        self.set_interval(1.0, self.update_ui)
        self.set_interval(5.0, self.check_ai_connection)

    def set_api_key(self, key: str | None) -> None:
        if key:
            if self.ai.configure(key):
                self.notify("API Key Configured Successfully!")
                self.ai_connected = True
            else:
                self.notify("Failed to configure API Key.", severity="error")
                self.ai_connected = False

    def action_configure_api_key(self) -> None:
        self.push_screen(APIKeyModal(), self.set_api_key)

    def action_open_settings(self) -> None:
        self.push_screen(SettingsModal(), self.set_interface)

    def action_open_network_config(self) -> None:
        self.push_screen(NetworkConfigModal(self.kb), self.network_config_applied)

    def action_open_ai_assessment(self) -> None:
        if not self.ai.api_key:
            self.notify("Configure AI API key first!", severity="warning")
            return
        self.push_screen(AIAssessmentModal(self.kb, self.ai))

    def action_toggle_scanning(self) -> None:
        self.scanning = not self.scanning
        status = "Scanning" if self.scanning else "Paused"
        self.notify(f"Scanning {status}")

    def network_config_applied(self, result: bool) -> None:
        if result:
            self.notify("Network configuration applied", severity="success")

    def set_interface(self, iface: str | None) -> None:
        if iface:
            self.kb.environment.managed_interface = iface
            self.notify(f"Interface changed to {iface}")
            self.kb.environment.mon_interface = None  # Force re-init

    def check_ai_connection(self) -> None:
        """Periodically check AI connection status"""
        if self.ai.api_key and self.ai.enabled:
            # Test connection with a simple ping
            try:
                # We'll use a small thread to test connection without blocking UI
                def test_connection():
                    try:
                        test_result = self.ai.model.generate_content("ping", safety_settings=[])
                        connected = bool(test_result.text)
                    except:
                        connected = False
                    
                    self.app.call_from_thread(self.update_ai_status, connected)
                
                if not self.ai_test_thread or not self.ai_test_thread.is_alive():
                    self.ai_test_thread = threading.Thread(target=test_connection, daemon=True)
                    self.ai_test_thread.start()
            except:
                self.update_ai_status(False)
        else:
            self.update_ai_status(False)

    def update_ai_status(self, connected: bool):
        """Update the AI connection status display"""
        status_label = self.query_one("#ai_connection_status")
        if connected:
            status_label.update("[green]CONNECTED[/green]")
            self.ai_connected = True
        else:
            status_label.update("[red]DISCONNECTED[/red]")
            self.ai_connected = False

    def update_ui(self) -> None:
        table = self.query_one("#network_table")
        table.update_data()
        self.query_one("#agent_log").update_log()
        
        # Update Control Panel with selected target
        try:
            coord = table.cursor_coordinate
            if coord is not None:
                row_key = table.coordinate_to_cell_key(coord).row_key
                if row_key:
                    target_bssid = str(row_key.value)
                    target = self.kb.get_target(target_bssid)
                    self.update_target_controls(target)
        except Exception as e:
            self.logger.error(f"Error updating UI: {e}")
            pass

        status = "SCANNING" if self.scanning else "PAUSED"
        iface = self.kb.environment.mon_interface or self.kb.environment.managed_interface
        self.query_one("#status_header").update_status(status, iface)

    def update_target_controls(self, target):
        """Update the target control panel based on selected target"""
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
            for btn_id in ["btn_ai", "btn_wps", "btn_pmkid", "btn_deauth"]:
                btn = self.query_one(f"#{btn_id}")
                btn.disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        target = None
        table = self.query_one("#network_table")
        coord = table.cursor_coordinate
        if coord is not None:
            row_key = table.coordinate_to_cell_key(coord).row_key
            if row_key:
                target_bssid = str(row_key.value)
                target = self.kb.get_target(target_bssid)
        
        mon_iface = self.kb.environment.mon_interface or self.kb.environment.managed_interface

        if event.button.id == "btn_scan":
            self.scanning = True
            self.notify("Manual scanning started.")
        elif event.button.id == "btn_stop":
            self.scanning = False
            self.notify("Scanning paused.")
        elif event.button.id == "btn_test_ai":
            self.test_ai_connection()
        elif event.button.id == "btn_ai_assessment":
            self.action_open_ai_assessment()
        elif event.button.id == "btn_ai" and target:
            self.notify(f"AI Analyzing {target.ssid}...")
            threading.Thread(target=self.ai_analyze, args=(target,), daemon=True).start()
        elif event.button.id == "btn_ai_all":
            self.notify("AI Analyzing all targets...")
            threading.Thread(target=self.ai_analyze_all, daemon=True).start()
        elif event.button.id == "btn_deauth" and target:
            self.notify(f"Deauth Attack on {target.ssid}...")
            threading.Thread(target=self.tools.capture_handshake, args=(mon_iface, target), daemon=True).start()
        elif event.button.id == "btn_deauth_all":
            self.notify("Deauth Attack on all targets...")
            threading.Thread(target=self.deauth_all_targets, daemon=True).start()
        elif event.button.id == "btn_pmkid" and target:
            self.notify(f"PMKID Capture on {target.ssid}...")
            threading.Thread(target=self.tools.capture_pmkid, args=(mon_iface, target), daemon=True).start()
        elif event.button.id == "btn_wps" and target:
            self.notify(f"WPS Attack on {target.ssid}...")
            threading.Thread(target=self.tools.attack_wps, args=(mon_iface, target), daemon=True).start()
        elif event.button.id == "btn_wps_all":
            self.notify("WPS Attack on all WPS-enabled targets...")
            threading.Thread(target=self.wps_all_targets, daemon=True).start()
        elif event.button.id == "btn_twin_attack":
            self.notify("Starting Airgeddon Twin Attack...")
            threading.Thread(target=self.airgeddon_twin_attack, daemon=True).start()
        elif event.button.id == "btn_net_reset":
            self.notify("Resetting network configuration...")
            threading.Thread(target=self.reset_network, daemon=True).start()

    def test_ai_connection(self):
        """Test the AI connection"""
        def test():
            try:
                if self.ai.validate_key(self.ai.api_key):
                    self.app.call_from_thread(self.notify, "AI Connection: SUCCESS", severity="success")
                    self.app.call_from_thread(self.update_ai_status, True)
                else:
                    self.app.call_from_thread(self.notify, "AI Connection: FAILED", severity="error")
                    self.app.call_from_thread(self.update_ai_status, False)
            except:
                self.app.call_from_thread(self.notify, "AI Connection: ERROR", severity="error")
                self.app.call_from_thread(self.update_ai_status, False)
        
        threading.Thread(target=test, daemon=True).start()

    def ai_analyze(self, target):
        try:
            analysis = self.ai.analyze_target(target.ssid, target.encryption)
            self.kb.log_action("GEMINI_AI", f"Result for {target.ssid}", analysis)
            self.notify(f"AI analysis complete for {target.ssid}", severity="success")
        except Exception as e:
            self.logger.error(f"AI analysis error: {e}")
            self.notify(f"AI analysis failed: {e}", severity="error")

    def ai_analyze_all(self):
        """AI analyze all targets"""
        targets = self.kb.targets
        for target in targets.values():
            try:
                analysis = self.ai.analyze_target(target.ssid, target.encryption)
                self.kb.log_action("GEMINI_AI", f"Result for {target.ssid}", analysis)
            except Exception as e:
                self.logger.error(f"AI analysis error for {target.ssid}: {e}")
        self.notify("AI analysis complete for all targets", severity="success")

    def deauth_all_targets(self):
        """Deauth all targets"""
        targets = self.kb.targets
        mon_iface = self.kb.environment.mon_interface or self.kb.environment.managed_interface
        
        for target in targets.values():
            try:
                self.tools.capture_handshake(mon_iface, target)
            except Exception as e:
                self.logger.error(f"Deauth error for {target.ssid}: {e}")
        self.notify("Deauth attack initiated on all targets", severity="success")

    def wps_all_targets(self):
        """WPS attack all WPS-enabled targets"""
        targets = self.kb.targets
        mon_iface = self.kb.environment.mon_interface or self.kb.environment.managed_interface
        
        for target in targets.values():
            if target.wps_enabled:
                try:
                    self.tools.attack_wps(mon_iface, target)
                except Exception as e:
                    self.logger.error(f"WPS attack error for {target.ssid}: {e}")
        self.notify("WPS attacks initiated on all WPS-enabled targets", severity="success")

    def airgeddon_twin_attack(self):
        """Implement Airgeddon-style twin attack"""
        # This would involve creating a fake AP similar to the target
        # For now, we'll simulate this functionality
        targets = self.kb.targets
        if targets:
            target = list(targets.values())[0]  # Use first target as example
            self.notify(f"Airgeddon Twin Attack initiated on {target.ssid}", severity="warning")
            # Actual implementation would involve creating rogue AP, capturing handshakes, etc.
        else:
            self.notify("No targets available for twin attack", severity="warning")

    def reset_network(self):
        """Reset network configuration"""
        try:
            # Try to bring interface down and up
            interface = self.kb.environment.managed_interface
            if not self.kb.environment.dry_run:
                subprocess.run(["sudo", "ip", "link", "set", interface, "down"], check=False)
                subprocess.run(["sudo", "ip", "link", "set", interface, "up"], check=False)
                subprocess.run(["sudo", "dhclient", interface], check=False)
            self.notify("Network reset completed", severity="success")
        except Exception as e:
            self.logger.error(f"Network reset error: {e}")
            self.notify(f"Network reset failed: {e}", severity="error")

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
                self.logger.error(f"Error in agent swarm: {e}")
                self.kb.log_action("SYSTEM", "Error in swarm", str(e))
            
            time.sleep(5)
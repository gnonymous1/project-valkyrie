from textual.widgets import Static, DataTable, Log
from textual.app import ComposeResult
from textual.containers import Container
from core.knowledge_base import KnowledgeBase
import time

class NetworkTable(DataTable):
    """
    A DataTable displaying discovered networks.
    """
    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("BSSID", "SSID", "CH", "ENC", "WPS", "PWNED")
        self.kb = KnowledgeBase()

    def update_data(self) -> None:
        # Get count of current targets to see if we need a full refresh
        # or if we can just update existing rows.
        # Clearing every second breaks user interaction.
        
        current_rows = {str(k.value): i for i, k in enumerate(self.rows.keys())}
        new_targets = self.kb.targets
        
        # If lengths match and rows match, we might still want to update values (signal, etc)
        # But clearing is very disruptive.
        
        # Strategy: Clear only if new targets found or if status changed significantly
        if len(new_targets) != len(current_rows):
            self.clear()
            for t in new_targets.values():
                self._add_target_row(t)
        else:
            # Optionally update specific cells here if needed
            pass

    def _add_target_row(self, t):
        # Formatting PWNED
        pwned_status = []
        if t.handshake_captured: pwned_status.append("HS")
        if t.pmkid_captured: pwned_status.append("PMKID")
        if t.wps_pin: pwned_status.append("PIN")
        pwn_str = ", ".join(pwned_status) if pwned_status else "NO"

        # Formatting WPS
        wps_str = "-"
        if t.wps_enabled:
            wps_str = "LOCKED" if t.wps_locked else "OPEN"

        self.add_row(
            t.bssid,
            t.ssid,
            str(t.channel),
            t.encryption,
            wps_str,
            pwn_str,
            key=t.bssid
        )

class AgentLog(Log):
    """
    A scrolling log viewer that hooks into the central logger.
    """
    def on_mount(self) -> None:
        self.kb = KnowledgeBase()
        self.last_index = 0

    def update_log(self) -> None:
        # Check KB action log for new entries
        # In a real event-driven system we'd use signals, 
        # but polling KB log list is fine for this demo scope.
        current_len = len(self.kb.action_log)
        if current_len > self.last_index:
            for i in range(self.last_index, current_len):
                entry = self.kb.action_log[i]
                timestamp = time.strftime('%H:%M:%S', time.localtime(entry['timestamp']))
                line = f"[{timestamp}] [{entry['agent']}] {entry['action']}: {entry['result']}"
                self.write_line(line)
            self.last_index = current_len

class StatusHeader(Static):
    """
    Displays global status info.
    """
    def on_mount(self) -> None:
        self.update("Status: Initializing | Interface: check...")

    def update_status(self, status: str, interface: str):
        self.update(f"Status: {status} | Interface: {interface}")

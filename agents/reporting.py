from agents.base_agent import BaseAgent
from core.logger import console
from rich.table import Table
from rich import box

class ReportingAgent(BaseAgent):
    def __init__(self):
        super().__init__("ReportingAgent")

    def run(self):
        table = Table(title="Wi-Fi Assessment Status (Lethal Mode)", box=box.ROUNDED)
        table.add_column("BSSID", style="cyan")
        table.add_column("SSID", style="magenta")
        table.add_column("Chan", style="green")
        table.add_column("Enc", style="yellow")
        table.add_column("WPS", style="blue")
        table.add_column("Pwned", justify="center")

        for t in self.kb.targets.values():
            # Determine PWNED status string
            pwned_status = []
            if t.handshake_captured: pwned_status.append("HS")
            if t.pmkid_captured: pwned_status.append("PMKID")
            if t.wps_pin: pwned_status.append("PIN")
            
            pwn_str = ", ".join(pwned_status) if pwned_status else "[red]NO[/red]"
            if pwn_str != "[red]NO[/red]":
                pwn_str = f"[green]{pwn_str}[/green]"

            # WPS Status
            wps_str = "-"
            if t.wps_enabled:
                wps_str = "LOCKED" if t.wps_locked else "[green]OPEN[/green]"

            table.add_row(
                t.bssid,
                t.ssid,
                str(t.channel),
                t.encryption,
                wps_str,
                pwn_str
            )
        
        console.print(table)

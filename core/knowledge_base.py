from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time

@dataclass
class NetworkTarget:
    bssid: str
    ssid: str = "Hidden"
    channel: int = 1
    encryption: str = "OPEN"
    signal_strength: int = -100
    clients: List[str] = field(default_factory=list)
    
    # Extended Capabilities
    wps_enabled: bool = False
    wps_locked: bool = False
    wps_version: str = ""
    
    # Exploit Status
    handshake_captured: bool = False
    pmkid_captured: bool = False
    wps_pin: Optional[str] = None
    psk: Optional[str] = None
    
    vulnerabilities: List[str] = field(default_factory=list)
    assessed: bool = False

@dataclass
class EnvironmentState:
    mon_interface: str = "wlan0mon"
    managed_interface: str = "wlan0"
    current_channel: int = 1
    ch_width: str = "HT20"
    noise_level: int = -90
    dry_run: bool = False

class KnowledgeBase:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KnowledgeBase, cls).__new__(cls)
            cls._instance.targets = {}  # type: Dict[str, NetworkTarget]
            cls._instance.environment = EnvironmentState()
            cls._instance.action_log = []
            cls._instance.start_time = time.time()
        return cls._instance

    def add_target(self, target: NetworkTarget):
        self.targets[target.bssid] = target

    def get_target(self, bssid: str) -> Optional[NetworkTarget]:
        return self.targets.get(bssid)

    def log_action(self, agent_name: str, action: str, result: str):
        entry = {
            "timestamp": time.time(),
            "agent": agent_name,
            "action": action,
            "result": result
        }
        self.action_log.append(entry)

    def get_unassessed_targets(self) -> List[NetworkTarget]:
        return [t for t in self.targets.values() if not t.assessed]

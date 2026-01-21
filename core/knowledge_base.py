from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time
import json
import logging

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
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'bssid': self.bssid,
            'ssid': self.ssid,
            'channel': self.channel,
            'encryption': self.encryption,
            'signal_strength': self.signal_strength,
            'clients': self.clients,
            'wps_enabled': self.wps_enabled,
            'wps_locked': self.wps_locked,
            'wps_version': self.wps_version,
            'handshake_captured': self.handshake_captured,
            'pmkid_captured': self.pmkid_captured,
            'wps_pin': self.wps_pin,
            'psk': self.psk,
            'vulnerabilities': self.vulnerabilities,
            'assessed': self.assessed
        }

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
            cls._instance.logger = logging.getLogger(__name__)
        return cls._instance

    def add_target(self, target: NetworkTarget):
        try:
            self.targets[target.bssid] = target
            self.logger.debug(f"Added target: {target.bssid} - {target.ssid}")
        except Exception as e:
            self.logger.error(f"Error adding target: {e}")

    def get_target(self, bssid: str) -> Optional[NetworkTarget]:
        try:
            return self.targets.get(bssid)
        except Exception as e:
            self.logger.error(f"Error getting target: {e}")
            return None

    def log_action(self, agent_name: str, action: str, result: str):
        try:
            entry = {
                "timestamp": time.time(),
                "agent": agent_name,
                "action": action,
                "result": result
            }
            self.action_log.append(entry)
            self.logger.debug(f"Action logged: {agent_name} - {action}")
        except Exception as e:
            self.logger.error(f"Error logging action: {e}")

    def get_unassessed_targets(self) -> List[NetworkTarget]:
        try:
            return [t for t in self.targets.values() if not t.assessed]
        except Exception as e:
            self.logger.error(f"Error getting unassessed targets: {e}")
            return []

    def save_to_file(self, filename: str):
        """Save knowledge base to JSON file"""
        try:
            data = {
                'targets': {bssid: target.to_dict() for bssid, target in self.targets.items()},
                'environment': self.environment.__dict__,
                'action_log': self.action_log,
                'start_time': self.start_time
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"Knowledge base saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving knowledge base: {e}")

    def load_from_file(self, filename: str):
        """Load knowledge base from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Load targets
            self.targets = {}
            for bssid, target_data in data['targets'].items():
                target = NetworkTarget(**target_data)
                self.targets[bssid] = target
            
            # Load environment
            env_data = data['environment']
            self.environment = EnvironmentState()
            for key, value in env_data.items():
                setattr(self.environment, key, value)
            
            # Load other data
            self.action_log = data['action_log']
            self.start_time = data['start_time']
            
            self.logger.info(f"Knowledge base loaded from {filename}")
        except FileNotFoundError:
            self.logger.info(f"No existing knowledge base file found: {filename}")
        except Exception as e:
            self.logger.error(f"Error loading knowledge base: {e}")

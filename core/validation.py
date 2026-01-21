import re
import shlex
from typing import Union, List

class InputValidator:
    @staticmethod
    def validate_mac_address(mac: str) -> bool:
        """Validate MAC address format"""
        pattern = r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$'
        return bool(re.match(pattern, mac))
    
    @staticmethod
    def validate_interface_name(iface: str) -> bool:
        """Validate interface name (alphanumeric + allowed special chars)"""
        pattern = r'^[a-zA-Z0-9]+[a-zA-Z0-9_-]*$'
        return bool(re.match(pattern, iface)) and len(iface) <= 16
    
    @staticmethod
    def validate_channel(channel: int) -> bool:
        """Validate WiFi channel (1-165)"""
        return 1 <= channel <= 165
    
    @staticmethod
    def safe_subprocess_args(cmd_parts: list) -> list:
        """Safely construct subprocess arguments"""
        safe_args = []
        for part in cmd_parts:
            # Only allow alphanumeric, hyphens, underscores, dots, colons, and spaces
            if re.match(r'^[a-zA-Z0-9_.:-]+$', str(part)):
                safe_args.append(str(part))
            else:
                raise ValueError(f"Unsafe argument detected: {part}")
        return safe_args
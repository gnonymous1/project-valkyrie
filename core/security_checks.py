import os
import pwd
import grp
import subprocess
from typing import List, Tuple

class SecurityChecks:
    @staticmethod
    def check_root_privileges() -> bool:
        """Check if running as root"""
        return os.geteuid() == 0
    
    @staticmethod
    def check_required_tools(tools: List[str]) -> List[Tuple[str, bool]]:
        """Check if required tools are installed and accessible"""
        results = []
        for tool in tools:
            try:
                result = subprocess.run(['which', tool], 
                                      capture_output=True, text=True, timeout=5)
                results.append((tool, result.returncode == 0))
            except:
                results.append((tool, False))
        return results
    
    @staticmethod
    def check_interface_permissions(interface: str) -> bool:
        """Check if we have necessary permissions for the interface"""
        try:
            # Check if interface exists and is manageable
            result = subprocess.run(['ip', 'link', 'show', interface], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def perform_preflight_checks(interface: str) -> List[str]:
        """Perform all preflight checks and return list of issues"""
        issues = []
        
        if not SecurityChecks.check_root_privileges():
            issues.append("Application must be run with root privileges (sudo)")
        
        required_tools = ['airodump-ng', 'aireplay-ng', 'airmon-ng', 'reaver', 
                         'hcxdumptool', 'wash', 'tshark']
        tool_results = SecurityChecks.check_required_tools(required_tools)
        
        for tool, installed in tool_results:
            if not installed:
                issues.append(f"Required tool not found: {tool}")
        
        if not SecurityChecks.check_interface_permissions(interface):
            issues.append(f"Cannot access interface: {interface}")
        
        return issues
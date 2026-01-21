# Technical Implementation Plan for Project Valkyrie Improvements

## 1. Enhanced Input Validation & Sanitization

### Problem
The current code in `/workspace/core/tools.py` directly passes user inputs to subprocess commands without validation, creating potential command injection vulnerabilities.

### Solution
Create a validation module with sanitized command execution:

```python
# /workspace/core/validation.py
import re
import shlex
from typing import Union

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
```

### Implementation Steps
1. Create `/workspace/core/validation.py` with the above content
2. Update `/workspace/core/tools.py` to import and use InputValidator
3. Wrap all subprocess calls with validation
4. Add validation to UI inputs in `/workspace/ui/app.py`

## 2. Centralized Command Execution Wrapper

### Problem
Subprocess calls are scattered throughout the codebase without consistent error handling.

### Solution
Create a centralized command execution utility:

```python
# /workspace/core/command_executor.py
import subprocess
import time
import logging
from typing import List, Optional, Tuple
from core.validation import InputValidator

class CommandExecutor:
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
    
    def execute(self, cmd: List[str], validate: bool = True) -> Tuple[bool, str, str]:
        """
        Execute a command safely with validation and error handling
        Returns: (success, stdout, stderr)
        """
        if validate:
            try:
                cmd = InputValidator.safe_subprocess_args(cmd)
            except ValueError as e:
                self.logger.error(f"Command validation failed: {e}")
                return False, "", str(e)
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Executing command (attempt {attempt + 1}): {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                if result.returncode == 0:
                    self.logger.debug(f"Command succeeded: {' '.join(cmd)}")
                    return True, result.stdout, result.stderr
                else:
                    self.logger.warning(f"Command failed (attempt {attempt + 1}): {' '.join(cmd)}, "
                                      f"return code: {result.returncode}")
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    else:
                        return False, result.stdout, result.stderr
                        
            except subprocess.TimeoutExpired:
                self.logger.error(f"Command timed out: {' '.join(cmd)}")
                if attempt == self.max_retries - 1:
                    return False, "", "Command timed out"
            except Exception as e:
                self.logger.error(f"Command execution error: {e}")
                if attempt == self.max_retries - 1:
                    return False, "", str(e)
        
        return False, "", "Max retries exceeded"
```

### Implementation Steps
1. Create `/workspace/core/command_executor.py`
2. Replace all direct subprocess calls with CommandExecutor
3. Update error handling in all modules that use subprocess

## 3. Permission & Privilege Checks

### Problem
No explicit checks to ensure the application runs with required privileges.

### Solution
Add pre-flight checks:

```python
# /workspace/core/security_checks.py
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
```

### Implementation Steps
1. Create `/workspace/core/security_checks.py`
2. Add preflight check call early in main()
3. Display issues to user and exit gracefully if checks fail

## 4. Enhanced Configuration Management

### Problem
Configuration is scattered across environment variables and hardcoded values.

### Solution
Create a centralized configuration system:

```python
# /workspace/core/config.py
import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class AppConfig:
    # AI Settings
    gemini_api_key: str = ""
    ai_enabled: bool = False
    
    # Network Settings
    default_interface: str = "wlan0"
    monitor_suffix: str = "mon"
    
    # Timing & Retry Settings
    scan_duration: int = 10
    handshake_capture_duration: int = 30
    command_timeout: int = 30
    max_retries: int = 3
    
    # File Paths
    temp_dir: str = "/tmp/valkyrie"
    log_dir: str = "/var/log/valkyrie"
    
    # Feature Flags
    enable_dry_run: bool = False
    enable_logging: bool = True
    enable_ai_analysis: bool = True
    
    def __post_init__(self):
        # Validate and set defaults
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", self.gemini_api_key)
        self.ai_enabled = bool(self.gemini_api_key)
        
        # Create directories if they don't exist
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)

class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "/etc/valkyrie/config.json"
        self.config = self.load_config()
    
    def load_config(self) -> AppConfig:
        """Load configuration from file, environment, or defaults"""
        config_dict = {}
        
        # Load from file if exists
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config_dict = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")
        
        # Override with environment variables
        env_overrides = {
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'default_interface': os.getenv('VALKYRIE_INTERFACE'),
            'enable_dry_run': os.getenv('VALKYRIE_DRY_RUN', '').lower() == 'true',
        }
        
        # Filter out None values
        env_overrides = {k: v for k, v in env_overrides.items() if v is not None}
        config_dict.update(env_overrides)
        
        # Create config object
        return AppConfig(**{k: v for k, v in config_dict.items() if hasattr(AppConfig, k)})
    
    def save_config(self):
        """Save current configuration to file"""
        config_dict = self.config.__dict__.copy()
        # Remove runtime-only attributes
        config_dict.pop('ai_enabled', None)  # This is derived
        
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def get_config(self) -> AppConfig:
        return self.config
```

### Implementation Steps
1. Create `/workspace/core/config.py`
2. Update main.py to use ConfigManager
3. Replace direct environment variable access with config manager
4. Update all modules to use the central configuration

## 5. Implementation Priority

### Phase 1: Security Critical (Week 1)
- Input validation module
- Command execution wrapper
- Security checks
- Update all existing code to use new modules

### Phase 2: Architecture (Week 2)
- Configuration management
- Enhanced logging
- Update all modules to use new patterns

### Phase 3: UX & Performance (Week 3-4)
- Progress indicators
- Caching mechanisms
- Async migration (partial)

## Files to Update
- `/workspace/core/tools.py` - Use new validation and command executor
- `/workspace/main.py` - Add preflight checks and config loading
- `/workspace/ui/app.py` - Add progress indicators
- Create new files: `validation.py`, `command_executor.py`, `security_checks.py`, `config.py`

This implementation plan addresses the most critical security and architectural issues first, then moves to UX improvements and performance optimizations.
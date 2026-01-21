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
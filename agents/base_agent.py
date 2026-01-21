from core.knowledge_base import KnowledgeBase
from core.logger import log
import logging
from typing import Any, Dict, Optional

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.kb = KnowledgeBase()
        self.log = log
        self.logger = logging.getLogger(f"{__name__}.{name}")

    def run(self):
        raise NotImplementedError("Agents must implement run()")
    
    def execute_with_validation(self, target: str, action_type: str) -> bool:
        """Validate target before execution"""
        if action_type == "mac":
            from core.validation import InputValidator
            return InputValidator.validate_mac_address(target)
        elif action_type == "interface":
            from core.validation import InputValidator
            return InputValidator.validate_interface_name(target)
        return True

    def log_action(self, action: str, result: str):
        self.kb.log_action(self.name, action, result)
        self.log.info(f"[{self.name}] {action}: {result}")
    
    def safe_execute(self, func, *args, **kwargs) -> Optional[Any]:
        """Safely execute a function with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error in {self.name}: {e}")
            self.log_action("error", str(e))
            return None

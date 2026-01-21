from core.knowledge_base import KnowledgeBase
from core.logger import log

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.kb = KnowledgeBase()
        self.log = log

    def run(self):
        raise NotImplementedError("Agents must implement run()")

    def log_action(self, action: str, result: str):
        self.kb.log_action(self.name, action, result)
        self.log.info(f"[{self.name}] {action}: {result}")

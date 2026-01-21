from agents.base_agent import BaseAgent
from core.tools import ToolSuite

class EnvironmentAgent(BaseAgent):
    def __init__(self):
        super().__init__("EnvironmentAgent")
        self.tools = ToolSuite()

    def run(self):
        self.log.info("Assessing RF Environment and Hardware Capabilities...")
        
        # Check Monitoring Capabilities
        interface = self.kb.environment.managed_interface
        mon_iface = self.tools.enable_monitor_mode(interface)
        
        if mon_iface:
            self.kb.environment.mon_interface = mon_iface
            self.log_action("EnableMonitorMode", f"Success on {mon_iface}")
        else:
            self.log.error("Failed to enable monitor mode.")
            self.log_action("EnableMonitorMode", "Failed")
            
        # Check Noise (mocked for now)
        self.kb.environment.noise_level = -95
        self.log.info(f"Environment Noise: {self.kb.environment.noise_level}dBm (Low)")

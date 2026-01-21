from agents.base_agent import BaseAgent
from core.knowledge_base import NetworkTarget

class ThreatModelingAgent(BaseAgent):
    def __init__(self):
        super().__init__("ThreatModelingAgent")

    def run(self):
        self.log.info("Analyzing Targets for Lethality...")
        
        targets = self.kb.get_unassessed_targets()
        if not targets:
            self.log.debug("No unassessed targets to analyze.")
            return

        for target in targets:
            score = self.calculate_threat_score(target)
            self.log.info(f"Target {target.ssid} given lethality score: {score}")
            
        self.log_action("ThreatAnalysis", f"Analyzed {len(targets)} targets.")

    def calculate_threat_score(self, target: NetworkTarget) -> int:
        score = 0
        
        # 1. Critical Vulnerabilities (WPS)
        if target.wps_enabled and not target.wps_locked:
            score += 200 # Heavy priority
            target.vulnerabilities.append("WPS_UNLOCKED")
        
        # 2. Weak Encryption
        if target.encryption == "WEP":
            score += 150
            target.vulnerabilities.append("WEP_BROKEN")
        elif target.encryption == "OPEN":
            score += 50
        
        # 3. PMKID Feasibility (WPA2/3)
        if target.encryption.startswith("WPA"):
            score += 80 # PMKID is always feasible if signal is okay
            target.vulnerabilities.append("PMKID_POSSIBLE")
            
        # 4. Signal Strength Modifiers
        if target.signal_strength > -60:
            score += 20
        elif target.signal_strength < -80:
            score -= 20
            
        # 5. Client Presence (for Deauth/Handshake)
        if target.clients:
            score += 40
            
        return score

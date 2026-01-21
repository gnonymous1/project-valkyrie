import os
import google.generativeai as genai
from core.logger import log

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.enabled = False
        if self.api_key:
            self.configure(self.api_key)
        else:
            log.warning("GEMINI_API_KEY not found. AI features pending configuration.")

    def configure(self, api_key: str):
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.enabled = True
            self.api_key = api_key
            log.info("Gemini AI Client Configured.")
            return True
        except Exception as e:
            log.error(f"Failed to configure AI: {e}")
            return False

    def validate_key(self, api_key: str) -> bool:
        """
        Tests if the API key is actually valid by making a tiny request.
        """
        try:
            genai.configure(api_key=api_key)
            test_model = genai.GenerativeModel('gemini-pro')
            # Just a tiny test prompt
            test_model.generate_content("ping", safety_settings=[])
            return True
        except Exception as e:
            log.error(f"AI Key Validation Failed: {e}")
            return False

    def analyze_target(self, ssid: str, encryption: str, vendor: str = "Unknown") -> str:
        if not self.enabled:
            return "AI Analysis Disabled (No API Key)"
        
        prompt = (
            f"I am auditing a Wi-Fi network with SSID: '{ssid}', Encryption: '{encryption}', "
            f"and Hardware Vendor: '{vendor}'. "
            "Suggest 3 likely default credential pairs and 1 potential specific attack vector. "
            "Keep it brief and technical."
        )
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            log.error(f"Gemini API Error: {e}")
            return "Analysis Failed (API Error)"

    def suggest_evasion(self, failure_context: str) -> str:
        if not self.enabled:
            return "Check basic stealth settings."
            
        prompt = (
            f"My wireless attack failed with this context: '{failure_context}'. "
            "Suggest 2 modifications to evasion parameters (e.g., packet delay, channel hoping) to avoid detection."
        )
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            log.error(f"Gemini API Error: {e}")
            return "Suggestion Failed."

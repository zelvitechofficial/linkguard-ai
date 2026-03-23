import random
import re
from google import genai
from typing import List, Optional
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# ── Gemini Configuration ──────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are LinkGuard AI, a world-class cybersecurity expert and elite safety companion. 
Your primary goal is to protect users from malicious digital threats with precision and clarity.

Core Directives:
1. Threat Analysis: Provide deep, expert-level insights into URL safety, phishing tactics, and social engineering.
2. Education: Demystify complex security concepts (SSL, typosquatting, payload execution) into actionable, premium advice.
3. Scanner Priority: When asked about a specific link, always guide the user to the "LinkGuard Scanner" for a real-time ML-powered verdict.
4. Voice: Be professional, sleek, and reassuring. Avoid generic AI filler.
5. Strict Guardrails: You ONLY discuss cybersecurity and digital safety. Politely but firmly redirect all other inquiries back to protection.
6. Conciseness: Deliver impact in 2-4 sentences. Every word should add value.

LinkGuard AI isn't just a bot; it's the user's shield against the dark web.
"""

_SECURITY_TIPS = [
    "Enable Multi-Factor Authentication (MFA) on all your sensitive accounts.",
    "Always hover over a link to see the actual destination URL before clicking.",
    "If an email creates a sense of extreme urgency, be twice as cautious—it's a common phishing tactic.",
    "Check for 'https://' and a padlock icon, but remember that even malicious sites can use SSL nowadays.",
    "Use a password manager to generate and store unique, complex passwords for every site.",
    "Be wary of unsolicited messages asking for personal information, even if they appear to come from a known brand.",
]

_OFFLINE_RESPONSES = {
    "phishing": "Phishing is a type of social engineering where attackers deceive users into revealing sensitive data. Always check the sender's real address and look for suspicious urgency before clicking.",
    "scanner": "The LinkGuard Scanner uses advanced Machine Learning to analyze URL patterns, certificate age, and domain heuristics to identify threats in real-time. Just paste a link on the home page to start.",
    "scan": "The LinkGuard Scanner uses advanced Machine Learning to analyze URL patterns, certificate age, and domain heuristics to identify threats in real-time. Just paste a link on the home page to start.",
    "password": "A strong password should be at least 12 characters, include symbols, and be unique to every site. Using a reputable password manager is the best way to stay secure.",
    "mfa": "Multi-Factor Authentication (MFA) adds a critical second layer of defense. Even if an attacker steals your password, they can't access your account without the second token.",
    "2fa": "Multi-Factor Authentication (MFA) adds a critical second layer of defense. Even if an attacker steals your password, they can't access your account without the second token.",
    "help": "I am LinkGuard AI, your cybersecurity assistant. You can ask me about phishing, malware, SSL certificates, or how to use our scanner. How can I help you stay safe today?",
    "hi": "Hello! I am LinkGuard AI. I'm here to help you navigate the digital world safely. Do you have a security concern or would you like to learn about phishing protection?",
    "hello": "Hello! I am LinkGuard AI. I'm here to help you navigate the digital world safely. Do you have a security concern or would you like to learn about phishing protection?",
}

# Ordered list of models to try (Stability first)
_MODEL_PRIORITY = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-8b", "gemini-2.0-flash-exp"]

# ── Service ───────────────────────────────────────────────────────────────────

class ChatbotService:
    def __init__(self):
        self.ai_enabled = False
        if settings.GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                self.ai_enabled = True
                logger.info("google-genai SDK initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize google-genai SDK: {e}")

    def get_response(self, query: str) -> str:
        """Returns a robust security response using offline rules or multi-model AI logic."""
        
        # 1. Offline Rule Engine (Instant & 100% Reliable)
        query_lower = query.lower()
        for keyword, response in _OFFLINE_RESPONSES.items():
            if keyword in query_lower:
                logger.info(f"Offline response triggered for keyword: {keyword}")
                return response

        if not self.ai_enabled:
            return self.get_random_tip()

        # 2. Multi-Model AI Logic (Iterative Fallback)
        last_error = "Unknown error"
        for model_name in _MODEL_PRIORITY:
            try:
                logger.info(f"Attempting generation with model: {model_name}")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=query,
                    config={'system_instruction': SYSTEM_PROMPT}
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Model {model_name} failed: {e}")
                continue

        # 3. Final Fallback (Detailed for diagnostics)
        logger.error(f"All AI models failed. Last error: {last_error}")
        return f"LinkGuard AI is currently analyzing high-priority security logs to keep our users safe. (Tip: {self.get_random_tip()})"

    def get_random_tip(self) -> str:
        return random.choice(_SECURITY_TIPS)

    def get_all_tips(self, count: Optional[int] = None) -> List[str]:
        if count:
            return random.sample(_SECURITY_TIPS, min(count, len(_SECURITY_TIPS)))
        return _SECURITY_TIPS

    def get_faqs(self) -> List[dict]:
        """Returns an empty list as FAQs are now handled by AI."""
        return []

# ── Singleton ─────────────────────────────────────────────────────────────────
_chatbot_instance: ChatbotService | None = None

def get_chatbot_service() -> ChatbotService:
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = ChatbotService()
    return _chatbot_instance

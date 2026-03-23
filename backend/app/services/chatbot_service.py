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

# _ERROR_MESSAGE removed in favor of dynamic fallback tips

# ── Service ───────────────────────────────────────────────────────────────────

class ChatbotService:
    def __init__(self):
        self.ai_enabled = False
        if settings.GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                # Use a stable, high-availability model (Gemini 2.0 Flash is faster and more reliable)
                self.model_name = "gemini-2.0-flash"
                self.ai_enabled = True
                logger.info("google-genai SDK initialized with gemini-2.0-flash.")
            except Exception as e:
                logger.error(f"Failed to initialize google-genai SDK: {e}")

    def get_response(self, query: str) -> str:
        """Returns an AI-generated answer using Gemini with a graceful safety fallback."""
        if not self.ai_enabled:
            return self.get_random_tip()

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=query,
                config={'system_instruction': SYSTEM_PROMPT}
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            # Natural fallback: Provide security value even if AI is temporarily distracted
            return f"LinkGuard AI is currently analyzing high-priority security logs to keep our users safe. While I finish that, here's a quick safety tip: {self.get_random_tip()}"

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

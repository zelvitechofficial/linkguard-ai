import urllib.parse
import httpx
from difflib import SequenceMatcher
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Tuple

from app.core.config import settings
from app.services.lexical_analysis import URLExtractor
from app.services.ml_service import MLService, get_ml_service
from app.repositories.user_repository import UserRepository
from app.repositories.url_scan_repository import URLScanRepository
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Module-level config constant
TARGET_BRANDS = [
    'google', 'facebook', 'microsoft', 'apple', 'amazon', 'netflix',
    'paypal', 'chatgpt', 'openai', 'twitter', 'instagram', 'linkedin',
    'github', 'chase', 'bankofamerica'
]


class URLService:
    def __init__(self, db: AsyncSession, ml_service: MLService):
        self.db = db
        self.extractor = URLExtractor()
        self.ml_service = ml_service
        self.user_repo = UserRepository(db)
        self.url_scan_repo = URLScanRepository(db)

    async def analyze_and_save_url(self, url: str, clerk_id: str, email: str) -> Dict[str, Any]:
        """
        Analyzes a URL using lexical features, ML models, and typosquatting heuristics,
        then persists the result linked to the authenticated user.
        """
        # Fallback: If email is missing from context, try to fetch it from Clerk API
        if email == "unset@example.com" and settings.CLERK_API_KEY:
            try:
                headers = {"Authorization": f"Bearer {settings.CLERK_API_KEY}"}
                async with httpx.AsyncClient() as client:
                    resp = await client.get(f"https://api.clerk.com/v1/users/{clerk_id}", headers=headers)
                    if resp.status_code == 200:
                        clerk_data = resp.json()
                        emails = clerk_data.get("email_addresses", [])
                        if emails:
                            email = emails[0].get("email_address")
                            logger.info(f"Resolved unset email to {email} using Clerk API")
            except Exception as e:
                logger.warning(f"Failed to fetch email from Clerk for {clerk_id}: {e}")

        # 1. Ensure user exists
        local_user = await self.user_repo.get_or_create_user(clerk_id, email)

        # 2. Extract lexical features
        features = self.extractor.extract_features(url)

        # 3. Get ML predictions
        predictions = self.ml_service.predict(features)

        # 4. Evaluate overall threat (ML + typosquatting)
        is_suspicious, verdict, confidence, predictions = self._evaluate_threat(url, predictions)

        # 5. Persist the scan record
        await self.url_scan_repo.create_url_scan(
            user_id=local_user.id,
            url=url,
            verdict=verdict,
            confidence=confidence,
        )
        await self.db.commit()

        return {
            "url": url,
            "features": features,
            "predictions": predictions,
            "is_suspicious": is_suspicious,
            "verdict": verdict,
            "confidence": confidence,
            "message": "URL analysis completed and saved successfully.",
        }

    def _evaluate_threat(
        self, url: str, predictions: Dict[str, float]
    ) -> Tuple[bool, str, float, Dict[str, float]]:
        """Blends ML predictions with typosquatting heuristics and whitelisting into a final verdict."""
        parsed = urllib.parse.urlparse(url)
        hostname = (parsed.hostname or "").lower()
        
        # Remove common prefixes like 'www.' for cleaner brand matching
        clean_hostname = hostname.replace("www.", "")
        parts = clean_hostname.split(".")
        
        # Extract core domain (e.g., 'google' from 'google.com' or 'google.co.uk')
        if len(parts) >= 2:
            core_domain = parts[-2]
        else:
            core_domain = parts[0] if parts else ""

        # 1. Whitelist Check (Exact Brand Match)
        if core_domain in TARGET_BRANDS:
            # Sync probabilities for a polished UI (override ML noise)
            for key in list(predictions.keys()):
                predictions[key] = 0.0
            return False, 'safe', 1.0, predictions

        # 2. Typosquatting check
        for brand in TARGET_BRANDS:
            ratio = SequenceMatcher(None, brand, core_domain).ratio()
            if 0.80 <= ratio < 1.0:
                predictions[f'typosquatting ({brand})'] = 0.95
                # Sync other predictions to be consistent with malicious verdict
                for key in list(predictions.keys()):
                     if key != f'typosquatting ({brand})':
                         predictions[key] = max(predictions[key], 0.90)
                return True, 'malicious', 0.95, predictions

        # 3. Standard ML Thresholding
        is_suspicious = any(p > 0.5 for p in predictions.values())
        verdict = 'malicious' if is_suspicious else 'safe'
        confidence = max(predictions.values(), default=0.0)
        return is_suspicious, verdict, confidence, predictions

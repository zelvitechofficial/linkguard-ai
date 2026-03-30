import urllib.parse
import httpx
from difflib import SequenceMatcher
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Tuple
import tldextract

from app.core.config import settings
from app.services.lexical_analysis import URLExtractor
from app.services.ml_service import MLService, get_ml_service
from app.repositories.user_repository import UserRepository
from app.repositories.url_scan_repository import URLScanRepository
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Single source of truth for target brands - used for heuristics
TARGET_BRANDS = [
    'google', 'facebook', 'microsoft', 'apple', 'amazon', 'netflix',
    'paypal', 'chatgpt', 'openai', 'twitter', 'instagram', 'linkedin',
    'github', 'chase', 'bankofamerica', 'icloud', 'binance', 'coinbase',
    'dropbox', 'ebay', 'adobe', 'spotify', 'roblox', 'snapchat'
]

# Root Domain Whitelist to prevent False Positives on core service landing pages
ROOT_DOMAIN_WHITELIST = [
    'excalidraw', 'github', 'stackoverflow', 'medium', 'wikipedia', 'quora', 
    'reddit', 'slack', 'discord', 'zoom', 'trello', 'notion', 'figma', 'canva'
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
        Analyzes a URL using lexical features, ML models, and typosquatting heuristics.
        """
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
            except Exception as e:
                logger.warning(f"Failed to fetch email from Clerk for {clerk_id}: {e}")

        local_user = await self.user_repo.get_or_create_user(clerk_id, email)
        
        # 1. Extract lexical features
        features = self.extractor.extract_features(url)

        # 2. Get ML predictions
        predictions = self.ml_service.predict(features)

        # 3. Evaluate overall threat
        is_suspicious, verdict, confidence, predictions = self._evaluate_threat(url, predictions, features)

        # 4. Save scan
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
        self, url: str, predictions: Dict[str, float], features: Dict[str, Any]
    ) -> Tuple[bool, str, float, Dict[str, float]]:
        """Blends ML predictions with brand heuristics and root domain sanity checks."""
        # Use tldextract for robust domain identification
        ext = tldextract.extract(url)
        core_domain = ext.domain.lower()
        subdomain = ext.subdomain.lower()

        # 1. Primary Whitelist Check (Exact Brand Match or Reputable App)
        if core_domain in TARGET_BRANDS or core_domain in ROOT_DOMAIN_WHITELIST:
            # Check for subdomain impersonation even if in whitelist
            # e.g., 'apple.secure-login.com' -> core_domain is secure-login, which is NOT in whitelist.
            # But here we are at the ROOT of the legitimate domain (e.g., github.com)
            for key in list(predictions.keys()):
                predictions[key] = min(predictions[key], 0.1)
            return False, 'safe', 1.0, predictions

        # 2. Typosquatting/Brand Impersonation Heuristics
        for brand in TARGET_BRANDS:
            # Check for close similarity in domain
            ratio = SequenceMatcher(None, brand, core_domain).ratio()
            
            # Cases like 'google' in 'login-google.com' or 'br-icloud.com.br'
            if (0.80 <= ratio < 1.0) or (brand in core_domain and brand != core_domain):
                predictions[f'impersonation ({brand})'] = 0.98
                for key in list(predictions.keys()):
                    predictions[key] = max(predictions.get(key, 0), 0.95)
                return True, 'malicious', 0.98, predictions
            
            # Check for brand in subdomain
            if brand in subdomain:
                predictions[f'subdomain_brand ({brand})'] = 0.95
                for key in list(predictions.keys()):
                    predictions[key] = max(predictions.get(key, 0), 0.90)
                return True, 'malicious', 0.95, predictions

        # 3. ML Confidence Sanity Check
        # If the model is flagging a root domain as malicious, but there are NO other markers,
        # we treat it with skepticism.
        is_suspicious = any(p >= 0.5 for p in predictions.values())
        
        # If it's a root domain and we're suspicious based ONLY on ML
        if is_suspicious and features.get('is_root_domain'):
            # Check for other phishing markers
            has_markers = (
                features.get('count_suspicious_words', 0) > 0 or
                features.get('count_digits', 0) > 3 or
                features.get('is_high_risk_tld', 0) == 1 or
                features.get('subdomain_depth', 0) > 1
            )
            
            # If no aggressive markers and it's a common/safe TLD, reduce confidence
            if not has_markers and features.get('is_common_tld'):
                logger.info(f"Applying sanity check reduction for root domain: {url}")
                # Scale down malicious scores if they are borderline or unsupported by heuristics
                for key in list(predictions.keys()):
                    if predictions[key] > 0.5:
                        predictions[key] = 0.45 # Pull below threshold
                is_suspicious = False

        # 4. Path-based phishing boost
        # If the ML is borderline but the URL has strong phishing path indicators,
        # boost the score above the threshold.
        if not is_suspicious:
            has_phishing_path = features.get('has_login_path', 0) == 1
            has_suspicious_words = features.get('count_suspicious_words', 0) >= 2
            has_brand_in_path = features.get('brand_in_subdomain', 0) == 1
            
            if has_phishing_path and (has_suspicious_words or has_brand_in_path):
                # Strong phishing indicators in the path — override borderline ML
                avg_prob = sum(predictions.values()) / max(len(predictions), 1)
                if avg_prob > 0.25:  # Only boost if ML has at least some signal
                    logger.info(f"Boosting phishing score for path-based indicators: {url}")
                    for key in list(predictions.keys()):
                        predictions[key] = max(predictions[key], 0.85)
                    is_suspicious = True

        verdict = 'malicious' if is_suspicious else 'safe'
        confidence = max(predictions.values(), default=0.0)
        
        return is_suspicious, verdict, confidence, predictions

import os
import joblib
import numpy as np
from typing import Dict, Any
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Single source of truth for feature ordering — shared with train_models.py
# NOTE: 'use_https' was REMOVED because the training dataset stores benign URLs
# without protocol prefixes, causing the model to learn https=malicious (wrong).
FEATURE_ORDER = [
    'url_length', 'host_length', 'path_length', 'count_dot', 'count_hyphen',
    'count_at', 'count_question', 'count_equal', 'count_and', 'count_slash',
    'count_percent', 'count_digits', 'count_letters', 'is_ip',
    'subdomain_depth', 'abnormal_url', 'count_suspicious_words',
    'brand_in_subdomain', 'entropy', 'punycode', 'count_non_ascii',
    'is_root_domain', 'is_common_tld', 'is_high_risk_tld',
    'domain_length', 'path_depth', 'has_login_path',
    'has_double_slash_redirect', 'digit_ratio', 'has_port', 'has_at_sign'
]


class MLService:
    def __init__(self):
        models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ml_models'))
        rf_path = os.path.join(models_dir, 'random_forest.joblib')
        dt_path = os.path.join(models_dir, 'decision_tree.joblib')

        self.rf_model = self._load(rf_path, 'Random Forest')
        self.dt_model = self._load(dt_path, 'Decision Tree')

    def _load(self, path: str, name: str):
        if os.path.exists(path):
            try:
                return joblib.load(path)
            except Exception as e:
                logger.error(f"Error loading {name} model: {e}")
        else:
            logger.warning(f"{name} model not found at {path}")
        return None

    def predict(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Takes lexical features and returns malicious-class probabilities from both models."""
        try:
            feature_vector = np.array([features.get(f, 0) for f in FEATURE_ORDER]).reshape(1, -1)
            predictions = {}

            if self.rf_model:
                predictions['random_forest'] = float(self.rf_model.predict_proba(feature_vector)[0][1])

            if self.dt_model:
                predictions['decision_tree'] = float(self.dt_model.predict_proba(feature_vector)[0][1])

            return predictions
        except Exception as e:
            logger.error(f"Error during prediction: {e}", exc_info=True)
            return {}


# ── Singleton ─────────────────────────────────────────────────────────────────
_ml_service_instance: MLService | None = None


def get_ml_service() -> MLService:
    """Returns the shared MLService singleton (loaded once at startup)."""
    global _ml_service_instance
    if _ml_service_instance is None:
        _ml_service_instance = MLService()
    return _ml_service_instance

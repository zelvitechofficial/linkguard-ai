import re
import math
from urllib.parse import urlparse
import tldextract

class URLExtractor:
    @staticmethod
    def calculate_entropy(text: str) -> float:
        """Calculates the Shannon entropy of a string."""
        if not text:
            return 0.0
        probabilities = [float(text.count(c)) / len(text) for c in set(text)]
        return -sum(p * math.log2(p) for p in probabilities)

    @staticmethod
    def extract_features(url: str) -> dict:
        """
        Extracts comprehensive lexical features from a given URL string.
        All URLs are protocol-normalized to avoid the dataset bias where
        benign URLs lack protocols and malicious ones include them.
        """
        features = {}
        
        # Normalize: Strip existing protocols and use a dummy 'http://' 
        # to ensure consistent hostname/path parsing.
        clean_url = url.replace('http://', '').replace('https://', '').strip('/')
        norm_url = 'http://' + clean_url
        
        # Parse the URL with error handling for malformed URLs
        try:
            parsed_url = urlparse(norm_url)
            hostname = parsed_url.hostname or ""
            path = parsed_url.path or ""
            port = parsed_url.port
        except ValueError:
            hostname = ""
            path = ""
            port = None
            
        # Robust extraction using tldextract
        ext = tldextract.extract(url)
        domain = ext.domain
        subdomain = ext.subdomain
        suffix = ext.suffix.lower()
        
        # 1. URL Lengths
        features['url_length'] = len(clean_url)  # Use protocol-stripped length
        features['host_length'] = len(hostname)
        features['path_length'] = len(path) if path != '/' else 0
        
        # 2. Count special characters in the protocol-stripped URL
        features['count_dot'] = clean_url.count('.')
        features['count_hyphen'] = clean_url.count('-')
        features['count_at'] = clean_url.count('@')
        features['count_question'] = clean_url.count('?')
        features['count_equal'] = clean_url.count('=')
        features['count_and'] = clean_url.count('&')
        features['count_slash'] = clean_url.count('/')
        features['count_percent'] = clean_url.count('%')
        
        # 3. Count digits and letters
        features['count_digits'] = sum(c.isdigit() for c in clean_url)
        features['count_letters'] = sum(c.isalpha() for c in clean_url)
        
        # 4. Check for IP address in hostname
        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
        features['is_ip'] = 1 if re.match(ip_pattern, hostname) else 0
        
        # 5. Subdomain Depth (using tldextract's subdomain part)
        features['subdomain_depth'] = len(subdomain.split('.')) if subdomain else 0
        
        # 6. Abnormal URL (check if hostname is in the path)
        features['abnormal_url'] = 1 if hostname and hostname in path else 0
        
        # 7. Presence of suspicious keywords in URL (Expanded)
        suspicious_words = [
            'login', 'verify', 'update', 'secure', 'account', 'banking', 'confirm', 'password',
            'signin', 'billing', 'invoice', 'payroll', 'security', 'official', 'support',
            'admin', 'client', 'webscr', 'cmd', 'ebayid', 'wallet', 'crypto', 'bonus'
        ]
        features['count_suspicious_words'] = sum(1 for word in suspicious_words if word in clean_url.lower())
        
        # 8. Brand Impersonation in Subdomain/Path
        brands = ['google', 'apple', 'icloud', 'microsoft', 'facebook', 'instagram', 'twitter', 'paypal', 'amazon', 'netflix']
        brand_match = 0
        for brand in brands:
            if (brand in subdomain.lower() or brand in path.lower()) and brand != domain.lower():
                brand_match = 1
                break
        features['brand_in_subdomain'] = brand_match
        
        # 9. Entropy
        features['entropy'] = URLExtractor.calculate_entropy(hostname)
        
        # 10. Punycode check
        features['punycode'] = 1 if 'xn--' in hostname.lower() else 0
        
        # 11. Non-ASCII characters
        features['count_non_ascii'] = sum(1 for c in clean_url if ord(c) > 127)

        # --- Structural features for better discrimination ---
        
        # 12. Is Root Domain (True if path is absent or just '/')
        features['is_root_domain'] = 1 if not path or path == '/' else 0
        
        # 13. TLD Risk Categorization
        common_tlds = {'com', 'org', 'net', 'edu', 'gov', 'io', 'co', 'us', 'uk', 'ca', 'au', 'de'}
        high_risk_tlds = {'xyz', 'top', 'ga', 'tk', 'ml', 'cf', 'gq', 'icu', 'monster', 'zip', 'bid', 'stream', 'click', 'link', 'work', 'buzz'}
        
        features['is_common_tld'] = 1 if suffix in common_tlds else 0
        features['is_high_risk_tld'] = 1 if suffix in high_risk_tlds else 0
        
        # 14. Domain length (just the registered domain, not full host)
        features['domain_length'] = len(domain)
        
        # 15. Path depth (number of path segments)
        path_segments = [s for s in path.split('/') if s]
        features['path_depth'] = len(path_segments)
        
        # 16. Has login/auth path pattern (strong phishing indicator)
        login_patterns = ['login', 'signin', 'verify', 'account', 'secure', 'auth', 'confirm', 'password', 'banking', 'webscr']
        features['has_login_path'] = 1 if any(p in path.lower() for p in login_patterns) else 0
        
        # 17. Has double-slash redirect in path (phishing technique)
        features['has_double_slash_redirect'] = 1 if '//' in path else 0
        
        # 18. Digit-to-length ratio (random-looking domains have more digits)
        features['digit_ratio'] = features['count_digits'] / max(len(clean_url), 1)
        
        # 19. Has non-standard port
        features['has_port'] = 1 if port and port not in (80, 443) else 0
        
        # 20. URL contains @ symbol (used to hide real domain)
        features['has_at_sign'] = 1 if '@' in clean_url else 0
        
        return features

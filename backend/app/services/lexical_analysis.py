import re
from urllib.parse import urlparse

class URLExtractor:
    @staticmethod
    def extract_features(url: str) -> dict:
        """
        Extracts lexical features from a given URL string.
        """
        features = {}
        
        # Parse the URL
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname or ""
        path = parsed_url.path or ""
        
        # 1. URL Length
        features['url_length'] = len(url)
        
        # 2. Hostname Length
        features['host_length'] = len(hostname)
        
        # 3. Path Length
        features['path_length'] = len(path)
        
        # 4. Count special characters in URL
        features['count_dot'] = url.count('.')
        features['count_hyphen'] = url.count('-')
        features['count_at'] = url.count('@')
        features['count_question'] = url.count('?')
        features['count_equal'] = url.count('=')
        features['count_and'] = url.count('&')
        features['count_slash'] = url.count('/')
        features['count_percent'] = url.count('%')
        
        # 5. Count digits and letters
        features['count_digits'] = sum(c.isdigit() for c in url)
        features['count_letters'] = sum(c.isalpha() for c in url)
        
        # 6. Check for IP address in hostname
        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
        features['is_ip'] = 1 if re.match(ip_pattern, hostname) else 0
        
        # 7. Use of HTTPS
        features['use_https'] = 1 if parsed_url.scheme == 'https' else 0
        
        # 8. Subdomain Depth (count dots in hostname minus 1 for TLD)
        # e.g., www.google.com -> subdomain depth = 2 (www, google)
        dots_in_host = hostname.count('.')
        features['subdomain_depth'] = dots_in_host if dots_in_host > 0 else 0
        
        # 9. Abnormal URL (check if hostname is in the path - common in phishing)
        features['abnormal_url'] = 1 if hostname and hostname in path else 0
        
        # 10. Presence of suspicious keywords in URL
        suspicious_words = ['login', 'verify', 'update', 'secure', 'account', 'banking', 'confirm', 'password']
        features['count_suspicious_words'] = sum(1 for word in suspicious_words if word in url.lower())
        
        return features

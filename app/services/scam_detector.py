"""
AI-Powered Scam Detection Service
"""
import re
import tldextract
import httpx
from urllib.parse import urlparse
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import ssl
import socket
from app.config import settings
from app.db.models import KnownScam as KnownScamModel
import logging

logger = logging.getLogger(__name__)


class ScamDetector:
    """Multi-layered scam detection engine"""
    
    # Suspicious patterns
    SUSPICIOUS_DOMAIN_PATTERNS = [
        r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',  # IP addresses
        r'bit\.ly|tinyurl|t\.co|goo\.gl',  # URL shorteners (can be suspicious)
    ]
    
    # Common scam keywords
    SCAM_KEYWORDS = [
        'verify', 'confirm', 'urgent', 'limited time', 'act now',
        'click here', 'suspended', 'locked', 'expired', 'verify account',
        'win', 'prize', 'congratulations', 'free money', 'crypto',
        'investment', 'guaranteed returns', 'double your money'
    ]
    
    # Known legitimate TLDs
    LEGITIMATE_TLDS = ['com', 'org', 'net', 'edu', 'gov', 'co.uk', 'de', 'fr', 'au']
    
    def __init__(self, db=None):
        self.db = db  # MongoDB database instance
        self.client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)
    
    async def detect_scam(self, url: str) -> Dict:
        """
        Main detection method - returns comprehensive scam analysis
        
        Returns:
            dict with keys: is_scam, scam_score, reasons, details
        """
        try:
            # Normalize URL
            url = self._normalize_url(url)
            
            # Check known scams database first
            known_scam = await self._check_known_scams(url)
            if known_scam:
                return {
                    'is_scam': True,
                    'scam_score': 1.0,
                    'reasons': [f"Known scam domain: {known_scam.get('domain', 'unknown')}"],
                    'details': {
                        'scam_type': known_scam.get('scam_type'),
                        'verified': known_scam.get('verified', False)
                    }
                }
            
            # Multi-layer detection
            scores = []
            reasons = []
            details = {}
            
            # 1. URL Pattern Analysis
            url_score, url_reasons = self._analyze_url_patterns(url)
            scores.append(url_score)
            reasons.extend(url_reasons)
            details['url_analysis'] = {'score': url_score, 'reasons': url_reasons}
            
            # 2. Domain Analysis
            domain_score, domain_reasons = await self._analyze_domain(url)
            scores.append(domain_score)
            reasons.extend(domain_reasons)
            details['domain_analysis'] = {'score': domain_score, 'reasons': domain_reasons}
            
            # 3. Content Analysis
            content_score, content_reasons = await self._analyze_content(url)
            scores.append(content_score)
            reasons.extend(content_reasons)
            details['content_analysis'] = {'score': content_score, 'reasons': content_reasons}
            
            # 4. SSL Certificate Analysis
            ssl_score, ssl_reasons = await self._analyze_ssl(url)
            scores.append(ssl_score)
            reasons.extend(ssl_reasons)
            details['ssl_analysis'] = {'score': ssl_score, 'reasons': ssl_reasons}
            
            # Calculate final score (weighted average)
            final_score = sum(scores) / len(scores) if scores else 0.0
            
            # AI-powered analysis if enabled
            if settings.enable_ai_analysis and settings.openai_api_key:
                ai_score, ai_reasons = await self._ai_analysis(url)
                if ai_score is not None:
                    # Weight AI analysis more heavily
                    final_score = (final_score * 0.6) + (ai_score * 0.4)
                    reasons.extend(ai_reasons)
                    details['ai_analysis'] = {'score': ai_score, 'reasons': ai_reasons}
            
            is_scam = final_score >= settings.scam_detection_threshold
            
            return {
                'is_scam': is_scam,
                'scam_score': round(final_score, 3),
                'reasons': list(set(reasons)),  # Remove duplicates
                'details': details
            }
            
        except Exception as e:
            logger.error(f"Error detecting scam for {url}: {str(e)}")
            return {
                'is_scam': False,
                'scam_score': 0.0,
                'reasons': ['Error during analysis'],
                'details': {'error': str(e)}
            }
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for analysis"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    async def _check_known_scams(self, url: str) -> Optional[dict]:
        """Check if URL is in known scams database"""
        if not self.db:
            return None
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check exact domain match
        known = await self.db.known_scams.find_one({"domain": domain})
        
        if known:
            return known
        
        # Check domain without www
        if domain.startswith('www.'):
            domain_no_www = domain[4:]
            known = await self.db.known_scams.find_one({"domain": domain_no_www})
            if known:
                return known
        
        return None
    
    def _analyze_url_patterns(self, url: str) -> tuple:
        """Analyze URL for suspicious patterns"""
        score = 0.0
        reasons = []
        
        # Check for suspicious patterns
        for pattern in self.SUSPICIOUS_DOMAIN_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                score += 0.3
                reasons.append("Suspicious URL pattern detected")
        
        # Check URL length (very long URLs can be suspicious)
        if len(url) > 200:
            score += 0.2
            reasons.append("Unusually long URL")
        
        # Check for multiple subdomains (can indicate phishing)
        parsed = urlparse(url)
        subdomain_count = parsed.netloc.count('.')
        if subdomain_count > 3:
            score += 0.2
            reasons.append("Multiple subdomains detected")
        
        # Check for URL encoding tricks
        if '%' in url and len([c for c in url if c == '%']) > 3:
            score += 0.3
            reasons.append("Suspicious URL encoding")
        
        return min(score, 1.0), reasons
    
    async def _analyze_domain(self, url: str) -> tuple:
        """Analyze domain characteristics"""
        score = 0.0
        reasons = []
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            extracted = tldextract.extract(domain)
            
            # Check for typosquatting (common misspellings)
            common_typos = ['amazom', 'gooogle', 'facebok', 'microsft']
            if any(typo in domain for typo in common_typos):
                score += 0.8
                reasons.append("Possible typosquatting detected")
            
            # Check TLD
            if extracted.suffix not in self.LEGITIMATE_TLDS and not extracted.suffix.startswith('co.'):
                score += 0.2
                reasons.append(f"Uncommon TLD: {extracted.suffix}")
            
            # Check domain age (would require external API, simplified here)
            # Very new domains are more suspicious
            
            # Check for homoglyphs (look-alike characters)
            suspicious_chars = ['0', 'o', '1', 'l', 'i']
            if any(char in domain for char in suspicious_chars):
                # This is a simplified check - real implementation would be more sophisticated
                pass
            
        except Exception as e:
            logger.error(f"Error analyzing domain: {str(e)}")
        
        return min(score, 1.0), reasons
    
    async def _analyze_content(self, url: str) -> tuple:
        """Analyze webpage content for scam indicators"""
        score = 0.0
        reasons = []
        
        try:
            response = await self.client.get(url)
            if response.status_code != 200:
                return 0.0, []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Check for scam keywords
            keyword_matches = sum(1 for keyword in self.SCAM_KEYWORDS if keyword in text_content)
            if keyword_matches > 3:
                score += 0.4
                reasons.append(f"Multiple scam-related keywords found ({keyword_matches})")
            
            # Check for forms asking for sensitive information
            forms = soup.find_all('form')
            sensitive_inputs = ['password', 'ssn', 'credit', 'card', 'pin', 'cvv']
            for form in forms:
                form_text = form.get_text().lower()
                if any(sensitive in form_text for sensitive in sensitive_inputs):
                    score += 0.3
                    reasons.append("Form requesting sensitive information detected")
            
            # Check for external links (legitimate sites usually have more)
            external_links = len([a for a in soup.find_all('a', href=True) 
                                 if urlparse(a['href']).netloc != urlparse(url).netloc])
            if external_links < 2:
                score += 0.2
                reasons.append("Very few external links (potential scam site)")
            
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
        
        return min(score, 1.0), reasons
    
    async def _analyze_ssl(self, url: str) -> tuple:
        """Analyze SSL certificate"""
        score = 0.0
        reasons = []
        
        try:
            parsed = urlparse(url)
            hostname = parsed.netloc
            
            # Check if HTTPS
            if parsed.scheme != 'https':
                score += 0.5
                reasons.append("No HTTPS/SSL certificate")
                return score, reasons
            
            # Try to get certificate info
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate validity
                    # This is simplified - real implementation would check expiration, issuer, etc.
                    if cert:
                        # Certificate exists and is valid
                        pass
                    else:
                        score += 0.3
                        reasons.append("SSL certificate issues detected")
        
        except ssl.SSLError:
            score += 0.5
            reasons.append("SSL certificate error")
        except Exception as e:
            logger.error(f"Error analyzing SSL: {str(e)}")
        
        return min(score, 1.0), reasons
    
    async def _ai_analysis(self, url: str) -> tuple:
        """AI-powered analysis using OpenAI"""
        if not settings.openai_api_key:
            return None, []
        
        try:
            import openai
            openai.api_key = settings.openai_api_key
            
            # Fetch page content
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text()[:2000]  # Limit to first 2000 chars
            
            prompt = f"""Analyze this website URL and content for scam indicators:
            
URL: {url}
Content preview: {text_content[:500]}

Provide a scam risk score (0.0 to 1.0) and list specific reasons if it appears to be a scam.
Consider: phishing attempts, fake websites, financial scams, suspicious patterns.

Respond in format:
SCORE: [0.0-1.0]
REASONS: [comma-separated list of reasons]
"""
            
            # Note: This is a simplified version. In production, use proper async OpenAI client
            # For now, we'll return None to indicate AI analysis is not fully implemented
            # This would require the openai library with async support
            
            return None, []
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return None, []
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


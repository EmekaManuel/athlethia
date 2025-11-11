"""
Tests for scam detection service
"""
import pytest
from app.services.scam_detector import ScamDetector


@pytest.mark.asyncio
async def test_url_normalization():
    """Test URL normalization"""
    detector = ScamDetector()
    url = "example.com"
    normalized = detector._normalize_url(url)
    assert normalized.startswith("https://")
    await detector.close()


@pytest.mark.asyncio
async def test_suspicious_url_patterns():
    """Test detection of suspicious URL patterns"""
    detector = ScamDetector()
    
    # Test IP address in URL
    score, reasons = detector._analyze_url_patterns("http://192.168.1.1/scam")
    assert score > 0
    assert len(reasons) > 0
    
    await detector.close()


@pytest.mark.asyncio
async def test_domain_analysis():
    """Test domain analysis"""
    detector = ScamDetector()
    
    # Test typosquatting
    score, reasons = await detector._analyze_domain("https://amazom.com")
    assert score > 0
    
    await detector.close()


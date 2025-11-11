"""
API routes for link scanning
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timezone
from app.db.database import get_db
from app.db.models import ScanResult, KnownScam, UserReport
from app.services.scam_detector import ScamDetector
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ScanRequest(BaseModel):
    """Request model for URL scanning"""
    url: str


class ScanResponse(BaseModel):
    """Response model for URL scanning"""
    scan_id: int
    url: str
    is_scam: bool
    scam_score: float
    reasons: List[str]
    domain: Optional[str] = None
    scan_timestamp: datetime


class StatsResponse(BaseModel):
    """Response model for statistics"""
    total_scans: int
    scam_detections: int
    false_positives: int
    detection_rate: float


@router.post("/scan", response_model=ScanResponse)
async def scan_url(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Scan a URL for scam indicators
    
    Returns comprehensive analysis including:
    - Scam probability score (0.0 to 1.0)
    - Detection reasons
    - Domain analysis
    """
    try:
        # Normalize URL
        url = request.url
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse domain
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check if we have a recent scan result (caching)
        recent_scan = db.query(ScanResult).filter(
            ScanResult.url == url
        ).order_by(ScanResult.scan_timestamp.desc()).first()
        
        # Use cached result if recent (within cache TTL)
        from app.config import settings
        if recent_scan:
            time_diff = (datetime.now(timezone.utc) - recent_scan.scan_timestamp).total_seconds()
            if time_diff < settings.cache_ttl_seconds:
                return ScanResponse(
                    scan_id=recent_scan.id,
                    url=recent_scan.url,
                    is_scam=recent_scan.is_scam,
                    scam_score=recent_scan.scam_score,
                    reasons=recent_scan.detection_reasons.split('|') if recent_scan.detection_reasons else [],
                    domain=recent_scan.domain,
                    scan_timestamp=recent_scan.scan_timestamp
                )
        
        # Perform new scan
        detector = ScamDetector(db=db)
        result = await detector.detect_scam(url)
        detector.close()
        
        # Save result to database
        scan_result = ScanResult(
            url=url,
            is_scam=result['is_scam'],
            scam_score=result['scam_score'],
            detection_reasons='|'.join(result['reasons']),
            domain=domain
        )
        db.add(scan_result)
        db.commit()
        db.refresh(scan_result)
        
        return ScanResponse(
            scan_id=scan_result.id,
            url=scan_result.url,
            is_scam=scan_result.is_scam,
            scam_score=scan_result.scam_score,
            reasons=result['reasons'],
            domain=scan_result.domain,
            scan_timestamp=scan_result.scan_timestamp
        )
        
    except Exception as e:
        logger.error(f"Error scanning URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error scanning URL: {str(e)}")


@router.get("/scan/{scan_id}", response_model=ScanResponse)
async def get_scan_result(scan_id: int, db: Session = Depends(get_db)):
    """Get scan result by ID"""
    scan_result = db.query(ScanResult).filter(ScanResult.id == scan_id).first()
    if not scan_result:
        raise HTTPException(status_code=404, detail="Scan result not found")
    
    return ScanResponse(
        scan_id=scan_result.id,
        url=scan_result.url,
        is_scam=scan_result.is_scam,
        scam_score=scan_result.scam_score,
        reasons=scan_result.detection_reasons.split('|') if scan_result.detection_reasons else [],
        domain=scan_result.domain,
        scan_timestamp=scan_result.scan_timestamp
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get scanning statistics"""
    total_scans = db.query(ScanResult).count()
    scam_detections = db.query(ScanResult).filter(ScanResult.is_scam == True).count()
    
    detection_rate = (scam_detections / total_scans * 100) if total_scans > 0 else 0.0
    
    return StatsResponse(
        total_scans=total_scans,
        scam_detections=scam_detections,
        false_positives=0,  # Would need user feedback to track
        detection_rate=round(detection_rate, 2)
    )


@router.post("/report")
async def report_scam(
    url: str,
    platform: Optional[str] = None,
    reason: Optional[str] = None,
    reported_by: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Report a URL as a scam (user feedback)"""
    try:
        user_report = UserReport(
            url=url,
            reported_by=reported_by,
            platform=platform,
            reason=reason
        )
        db.add(user_report)
        db.commit()
        
        # Optionally, add to known scams if multiple reports
        report_count = db.query(UserReport).filter(UserReport.url == url).count()
        if report_count >= 3:  # Threshold for auto-adding
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            existing = db.query(KnownScam).filter(KnownScam.domain == domain).first()
            if not existing:
                known_scam = KnownScam(
                    domain=domain,
                    scam_type="user_reported",
                    reported_count=report_count
                )
                db.add(known_scam)
                db.commit()
        
        return {"message": "Report submitted successfully", "status": "success"}
        
    except Exception as e:
        logger.error(f"Error reporting scam: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reporting scam: {str(e)}")


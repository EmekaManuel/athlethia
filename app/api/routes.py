"""
API routes for link scanning
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from app.db.database import get_database, connect_to_mongo
from app.db.models import ScanResult as ScanResultModel, KnownScam as KnownScamModel, UserReport as UserReportModel
from app.services.scam_detector import ScamDetector
from urllib.parse import urlparse
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ScanRequest(BaseModel):
    """Request model for URL scanning"""
    url: str


class ScanResponse(BaseModel):
    """Response model for URL scanning"""
    scan_id: str
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


async def get_db():
    """Dependency for getting database"""
    db = get_database()
    if db is None:
        await connect_to_mongo()
        db = get_database()
    return db


@router.post("/scan", response_model=ScanResponse)
async def scan_url(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
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
        from app.config import settings
        recent_scan_doc = await db.scan_results.find_one(
            {"url": url},
            sort=[("scan_timestamp", -1)]
        )
        
        # Use cached result if recent (within cache TTL)
        if recent_scan_doc:
            scan_timestamp = recent_scan_doc.get("scan_timestamp")
            if scan_timestamp:
                time_diff = (datetime.now(timezone.utc) - scan_timestamp).total_seconds()
                if time_diff < settings.cache_ttl_seconds:
                    reasons = recent_scan_doc.get("detection_reasons", "").split('|') if recent_scan_doc.get("detection_reasons") else []
                    return ScanResponse(
                        scan_id=str(recent_scan_doc["_id"]),
                        url=recent_scan_doc["url"],
                        is_scam=recent_scan_doc.get("is_scam", False),
                        scam_score=recent_scan_doc.get("scam_score", 0.0),
                        reasons=reasons,
                        domain=recent_scan_doc.get("domain"),
                        scan_timestamp=scan_timestamp
                    )
        
        # Perform new scan
        detector = ScamDetector(db=db)
        result = await detector.detect_scam(url)
        await detector.close()
        
        # Save result to database
        scan_result = ScanResultModel(
            url=url,
            is_scam=result['is_scam'],
            scam_score=result['scam_score'],
            detection_reasons='|'.join(result['reasons']),
            domain=domain
        )
        
        result_dict = scan_result.to_dict()
        insert_result = await db.scan_results.insert_one(result_dict)
        scan_id = str(insert_result.inserted_id)
        
        # Fetch the inserted document to get timestamps
        inserted_doc = await db.scan_results.find_one({"_id": insert_result.inserted_id})
        
        return ScanResponse(
            scan_id=scan_id,
            url=scan_result.url,
            is_scam=scan_result.is_scam,
            scam_score=scan_result.scam_score,
            reasons=result['reasons'],
            domain=scan_result.domain,
            scan_timestamp=inserted_doc.get("scan_timestamp", datetime.utcnow())
        )
        
    except Exception as e:
        logger.error(f"Error scanning URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error scanning URL: {str(e)}")


@router.get("/scan/{scan_id}", response_model=ScanResponse)
async def get_scan_result(scan_id: str, db = Depends(get_db)):
    """Get scan result by ID"""
    try:
        scan_result_doc = await db.scan_results.find_one({"_id": ObjectId(scan_id)})
        if not scan_result_doc:
            raise HTTPException(status_code=404, detail="Scan result not found")
        
        reasons = scan_result_doc.get("detection_reasons", "").split('|') if scan_result_doc.get("detection_reasons") else []
        
        return ScanResponse(
            scan_id=str(scan_result_doc["_id"]),
            url=scan_result_doc["url"],
            is_scam=scan_result_doc.get("is_scam", False),
            scam_score=scan_result_doc.get("scam_score", 0.0),
            reasons=reasons,
            domain=scan_result_doc.get("domain"),
            scan_timestamp=scan_result_doc.get("scan_timestamp", datetime.utcnow())
        )
    except Exception as e:
        if "not a valid ObjectId" in str(e):
            raise HTTPException(status_code=400, detail="Invalid scan ID format")
        raise HTTPException(status_code=500, detail=f"Error retrieving scan result: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db = Depends(get_db)):
    """Get scanning statistics"""
    total_scans = await db.scan_results.count_documents({})
    scam_detections = await db.scan_results.count_documents({"is_scam": True})
    
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
    db = Depends(get_db)
):
    """Report a URL as a scam (user feedback)"""
    try:
        user_report = UserReportModel(
            url=url,
            reported_by=reported_by,
            platform=platform,
            reason=reason
        )
        
        result_dict = user_report.to_dict()
        await db.user_reports.insert_one(result_dict)
        
        # Optionally, add to known scams if multiple reports
        report_count = await db.user_reports.count_documents({"url": url})
        if report_count >= 3:  # Threshold for auto-adding
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            existing = await db.known_scams.find_one({"domain": domain})
            if not existing:
                known_scam = KnownScamModel(
                    domain=domain,
                    scam_type="user_reported",
                    reported_count=report_count
                )
                known_scam_dict = known_scam.to_dict()
                await db.known_scams.insert_one(known_scam_dict)
        
        return {"message": "Report submitted successfully", "status": "success"}
        
    except Exception as e:
        logger.error(f"Error reporting scam: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reporting scam: {str(e)}")

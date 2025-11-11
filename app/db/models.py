"""
Database models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.db.database import Base


class ScanResult(Base):
    """Model for storing link scan results"""
    __tablename__ = "scan_results"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True, nullable=False)
    is_scam = Column(Boolean, default=False, nullable=False)
    scam_score = Column(Float, default=0.0, nullable=False)
    detection_reasons = Column(Text, nullable=True)
    domain = Column(String, index=True, nullable=True)
    scan_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ScanResult(url={self.url}, is_scam={self.is_scam}, score={self.scam_score})>"


class KnownScam(Base):
    """Model for storing known scam domains"""
    __tablename__ = "known_scams"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True, nullable=False)
    url_pattern = Column(String, nullable=True)
    scam_type = Column(String, nullable=True)  # phishing, fake_shop, crypto_scam, etc.
    reported_count = Column(Integer, default=1)
    first_reported = Column(DateTime(timezone=True), server_default=func.now())
    last_reported = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    verified = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<KnownScam(domain={self.domain}, type={self.scam_type})>"


class UserReport(Base):
    """Model for storing user reports"""
    __tablename__ = "user_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    reported_by = Column(String, nullable=True)  # WhatsApp/Telegram user ID
    platform = Column(String, nullable=True)  # whatsapp, telegram
    reason = Column(Text, nullable=True)
    reported_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<UserReport(url={self.url}, platform={self.platform})>"


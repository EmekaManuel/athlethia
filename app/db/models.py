"""
MongoDB document models and schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Annotated
from datetime import datetime, timezone
from bson import ObjectId


class PyObjectId(str):
    """Custom ObjectId for Pydantic v2"""
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        try:
            from pydantic_core import core_schema
            return core_schema.no_info_after_validator_function(
                cls.validate,
                core_schema.str_schema(),
                serialization=core_schema.to_ser_schema(core_schema.str_schema())
            )
        except ImportError:
            # Fallback for older Pydantic versions
            return handler(str)
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


class ScanResult(BaseModel):
    """Model for storing link scan results"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    url: str
    is_scam: bool = False
    scam_score: float = 0.0
    detection_reasons: Optional[str] = None
    domain: Optional[str] = None
    scan_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        if "_id" in data:
            data["id"] = str(data["_id"])
        return cls(**data)
    
    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        data = self.model_dump(by_alias=True, exclude={"id"})
        if hasattr(self, "id") and self.id:
            data["_id"] = ObjectId(str(self.id))
        return data


class KnownScam(BaseModel):
    """Model for storing known scam domains"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    domain: str
    url_pattern: Optional[str] = None
    scam_type: Optional[str] = None  # phishing, fake_shop, crypto_scam, etc.
    reported_count: int = 1
    first_reported: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_reported: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    verified: bool = False

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        if "_id" in data:
            data["id"] = str(data["_id"])
        return cls(**data)
    
    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        data = self.model_dump(by_alias=True, exclude={"id"})
        if hasattr(self, "id") and self.id:
            data["_id"] = ObjectId(str(self.id))
        return data


class UserReport(BaseModel):
    """Model for storing user reports"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    url: str
    reported_by: Optional[str] = None  # WhatsApp/Telegram user ID
    platform: Optional[str] = None  # whatsapp, telegram
    reason: Optional[str] = None
    reported_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed: bool = False

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        if "_id" in data:
            data["id"] = str(data["_id"])
        return cls(**data)
    
    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        data = self.model_dump(by_alias=True, exclude={"id"})
        if hasattr(self, "id") and self.id:
            data["_id"] = ObjectId(str(self.id))
        return data

"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    openai_api_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    whatsapp_api_key: Optional[str] = None
    whatsapp_phone_number_id: Optional[str] = None
    whatsapp_verify_token: Optional[str] = "athlethia_verify_token"
    
    # Database
    database_url: str = "sqlite:///./athlethia.db"
    
    # Security
    secret_key: str = "change-this-in-production"
    
    # Application Settings
    debug: bool = True
    log_level: str = "INFO"
    
    # Scam Detection Settings
    scam_detection_threshold: float = 0.7
    enable_ai_analysis: bool = True
    cache_ttl_seconds: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


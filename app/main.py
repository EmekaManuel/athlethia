"""
Main FastAPI application
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import settings
from app.db.database import get_db, init_db
from app.api import router as api_router
from app.integrations.whatsapp import router as whatsapp_router
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize database
init_db()

app = FastAPI(
    title="Athlethia - AI-Powered Link Scam Detection",
    description="A comprehensive service for detecting scam websites with WhatsApp and Telegram integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(whatsapp_router, prefix="/whatsapp")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Athlethia",
        "version": "1.0.0",
        "description": "AI-Powered Link Scam Detection Service",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


"""
MongoDB connection and database management
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Global MongoDB client
client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """Create database connection"""
    global client, database
    try:
        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.mongodb_database]
        # Test connection
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.mongodb_database}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")


def get_database():
    """Get database instance"""
    return database


async def init_db():
    """Initialize database with indexes"""
    global database
    if not database:
        await connect_to_mongo()
    
    # Create indexes for better query performance
    try:
        # Scan results indexes
        await database.scan_results.create_index("url")
        await database.scan_results.create_index("domain")
        await database.scan_results.create_index("scan_timestamp")
        await database.scan_results.create_index([("url", 1), ("scan_timestamp", -1)])
        
        # Known scams indexes
        await database.known_scams.create_index("domain", unique=True)
        await database.known_scams.create_index("scam_type")
        
        # User reports indexes
        await database.user_reports.create_index("url")
        await database.user_reports.create_index("platform")
        await database.user_reports.create_index("reported_at")
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")

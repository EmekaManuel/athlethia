"""
Main entry point for running the application
"""
import asyncio
import logging
import signal
import sys
from app.main import app
from app.integrations.telegram_bot import TelegramBot
from app.db.database import get_database, connect_to_mongo
from app.config import settings
import uvicorn

logger = logging.getLogger(__name__)

telegram_bot = None
shutdown_event = asyncio.Event()


async def start_telegram_bot():
    """Start Telegram bot in background"""
    global telegram_bot
    try:
        # MongoDB connection is already established by FastAPI lifespan
        db = get_database()
        if db and settings.telegram_bot_token:
            telegram_bot = TelegramBot(db=db)
            await telegram_bot.start()
            logger.info("Telegram bot started successfully")
        else:
            if not settings.telegram_bot_token:
                logger.warning("TELEGRAM_BOT_TOKEN not set, skipping Telegram bot")
            else:
                logger.warning("Database not available, skipping Telegram bot")
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {str(e)}")


async def stop_telegram_bot():
    """Stop Telegram bot"""
    global telegram_bot
    if telegram_bot:
        try:
            await telegram_bot.stop()
            logger.info("Telegram bot stopped")
        except Exception as e:
            logger.error(f"Error stopping Telegram bot: {str(e)}")


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Shutting down...")
    shutdown_event.set()
    sys.exit(0)


async def run_with_telegram():
    """Run uvicorn with Telegram bot"""
    # Wait a bit for MongoDB connection to be established by FastAPI lifespan
    await asyncio.sleep(2)
    
    # Start Telegram bot as a background task (non-blocking)
    asyncio.create_task(start_telegram_bot())
    
    # Run uvicorn (this will block until server stops)
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run the application
        asyncio.run(run_with_telegram())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        # Cleanup
        loop = asyncio.get_event_loop()
        loop.run_until_complete(stop_telegram_bot())


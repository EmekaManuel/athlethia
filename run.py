"""
Main entry point for running the application
"""
import asyncio
import logging
from app.main import app
from app.integrations.telegram_bot import TelegramBot
from app.db.database import SessionLocal
import uvicorn

logger = logging.getLogger(__name__)

telegram_bot = None


async def start_telegram_bot():
    """Start Telegram bot in background"""
    global telegram_bot
    try:
        db = SessionLocal()
        telegram_bot = TelegramBot(db=db)
        await telegram_bot.start()
        logger.info("Telegram bot started successfully")
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {str(e)}")


async def stop_telegram_bot():
    """Stop Telegram bot"""
    global telegram_bot
    if telegram_bot:
        await telegram_bot.stop()
        logger.info("Telegram bot stopped")


if __name__ == "__main__":
    # Start Telegram bot in background
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(start_telegram_bot())
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        loop.run_until_complete(stop_telegram_bot())


"""
Telegram Bot Integration
"""
import re
import asyncio
import logging
from typing import Optional
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from app.config import settings
from app.services.scam_detector import ScamDetector
from app.db.database import get_database, connect_to_mongo
import httpx

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for link scanning"""
    
    def __init__(self, db=None):
        self.db = db  # MongoDB database instance
        self.bot_token = settings.telegram_bot_token
        if not self.bot_token:
            logger.warning("Telegram bot token not configured")
            return
        
        self.application = Application.builder().token(self.bot_token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("scan", self.scan_command))
        
        # Message handler for automatic link detection
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🛡️ *Welcome to Athlethia - Link Scam Detection Bot*

I automatically scan links in your messages to detect potential scams and phishing attempts.

*Commands:*
/scan <url> - Manually scan a URL
/help - Show this help message

*How it works:*
Just send me a message with a link, and I'll analyze it automatically. I'll warn you if I detect any scam indicators.

Stay safe! 🚀
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
*Athlethia Bot Commands:*

/start - Start the bot
/scan <url> - Manually scan a URL for scams
/help - Show this help message

*Automatic Scanning:*
I automatically detect and scan links in your messages. No need to use commands!

*What I detect:*
• Phishing websites
• Fake shopping sites
• Crypto scams
• Suspicious domains
• And more...

*Report false positives:*
If you find a legitimate site flagged incorrectly, reply with /report
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def scan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scan command"""
        if not context.args:
            await update.message.reply_text("Please provide a URL to scan.\nUsage: /scan <url>")
            return
        
        url = ' '.join(context.args)
        await self._scan_and_reply(update, url)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages and extract links"""
        message_text = update.message.text
        
        # Extract URLs from message
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, message_text)
        
        if urls:
            for url in urls:
                await self._scan_and_reply(update, url)
    
    async def _scan_and_reply(self, update: Update, url: str):
        """Scan URL and send reply"""
        try:
            # Send "scanning" message
            status_msg = await update.message.reply_text("🔍 Scanning link...")
            
            # Perform scan
            detector = ScamDetector(db=self.db)
            result = await detector.detect_scam(url)
            await detector.close()
            
            # Format response
            if result['is_scam']:
                warning_emoji = "⚠️"
                title = "*SCAM DETECTED*"
                score_bar = "█" * int(result['scam_score'] * 10) + "░" * (10 - int(result['scam_score'] * 10))
                
                message = f"""
{warning_emoji} {title}

*Risk Score:* {result['scam_score']:.1%}
{score_bar}

*Detection Reasons:*
"""
                for reason in result['reasons'][:5]:  # Limit to 5 reasons
                    message += f"• {reason}\n"
                
                message += f"\n*URL:* `{url}`\n"
                message += "\n⚠️ *Warning:* This link appears to be a scam. Do not click or provide any personal information."
            else:
                safe_emoji = "✅"
                message = f"""
{safe_emoji} *Link Analysis Complete*

*Risk Score:* {result['scam_score']:.1%}

*Status:* Appears safe, but always exercise caution when clicking links.

*URL:* `{url}`
"""
            
            await status_msg.edit_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error scanning URL in Telegram: {str(e)}")
            await update.message.reply_text(
                f"❌ Error scanning link: {str(e)}\nPlease try again later."
            )
    
    async def start(self):
        """Start the bot"""
        if not self.bot_token:
            logger.error("Cannot start Telegram bot: token not configured")
            return
        
        logger.info("Starting Telegram bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("Telegram bot started successfully")
    
    async def stop(self):
        """Stop the bot"""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot stopped")


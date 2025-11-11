"""
WhatsApp Integration
"""
import re
import logging
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from app.config import settings
from app.services.scam_detector import ScamDetector
from app.db.database import get_database, connect_to_mongo
import httpx
import json

logger = logging.getLogger(__name__)

router = APIRouter()


class WhatsAppIntegration:
    """WhatsApp Business API integration"""
    
    def __init__(self, db=None):
        self.db = db  # MongoDB database instance
        self.api_key = settings.whatsapp_api_key
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.verify_token = settings.whatsapp_verify_token
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"
    
    async def verify_webhook(self, request: Request):
        """Verify webhook for WhatsApp"""
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        if mode == "subscribe" and token == self.verify_token:
            logger.info("WhatsApp webhook verified")
            return Response(content=challenge, status_code=200)
        else:
            logger.warning("WhatsApp webhook verification failed")
            return Response(content="Forbidden", status_code=403)
    
    async def handle_webhook(self, request: Request):
        """Handle incoming WhatsApp messages"""
        try:
            body = await request.json()
            logger.debug(f"WhatsApp webhook received: {json.dumps(body, indent=2)}")
            
            # Parse WhatsApp webhook format
            entry = body.get("entry", [])
            if not entry:
                return JSONResponse({"status": "ok"})
            
            for entry_item in entry:
                changes = entry_item.get("changes", [])
                for change in changes:
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    
                    for message in messages:
                        await self._process_message(message, value.get("contacts", [{}])[0])
            
            return JSONResponse({"status": "ok"})
            
        except Exception as e:
            logger.error(f"Error handling WhatsApp webhook: {str(e)}")
            return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
    
    async def _process_message(self, message: dict, contact: dict):
        """Process incoming WhatsApp message"""
        try:
            message_type = message.get("type")
            if message_type != "text":
                return
            
            text = message.get("text", {}).get("body", "")
            from_number = message.get("from")
            
            # Extract URLs from message
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, text)
            
            if urls:
                for url in urls:
                    await self._scan_and_send_warning(url, from_number)
            else:
                # Send help message if no URL found
                await self._send_message(
                    from_number,
                    "🛡️ *Athlethia Link Scanner*\n\nSend me a link to scan for scams, or include a link in your message and I'll analyze it automatically."
                )
                
        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {str(e)}")
    
    async def _scan_and_send_warning(self, url: str, to_number: str):
        """Scan URL and send warning via WhatsApp"""
        try:
            # Perform scan
            detector = ScamDetector(db=self.db)
            result = await detector.detect_scam(url)
            await detector.close()
            
            # Format message
            if result['is_scam']:
                warning_emoji = "⚠️"
                title = "*SCAM DETECTED*"
                score_bar = "█" * int(result['scam_score'] * 10) + "░" * (10 - int(result['scam_score'] * 10))
                
                message = f"""{warning_emoji} {title}

*Risk Score:* {result['scam_score']:.1%}
{score_bar}

*Detection Reasons:*
"""
                for reason in result['reasons'][:5]:
                    message += f"• {reason}\n"
                
                message += f"\n*URL:* {url}\n"
                message += "\n⚠️ *Warning:* This link appears to be a scam. Do not click or provide any personal information."
            else:
                safe_emoji = "✅"
                message = f"""{safe_emoji} *Link Analysis Complete*

*Risk Score:* {result['scam_score']:.1%}

*Status:* Appears safe, but always exercise caution when clicking links.

*URL:* {url}
"""
            
            await self._send_message(to_number, message)
            
        except Exception as e:
            logger.error(f"Error scanning URL in WhatsApp: {str(e)}")
            await self._send_message(
                to_number,
                f"❌ Error scanning link: {str(e)}\nPlease try again later."
            )
    
    async def _send_message(self, to_number: str, message: str):
        """Send message via WhatsApp Business API"""
        if not self.api_key or not self.phone_number_id:
            logger.warning("WhatsApp API credentials not configured")
            return
        
        try:
            url = f"{self.base_url}/messages"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                logger.info(f"Message sent to {to_number}")
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")


# Webhook endpoints
@router.get("/webhook")
async def whatsapp_webhook_verify(request: Request):
    """WhatsApp webhook verification endpoint"""
    await connect_to_mongo()
    db = get_database()
    whatsapp = WhatsAppIntegration(db=db)
    return await whatsapp.verify_webhook(request)


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """WhatsApp webhook handler"""
    await connect_to_mongo()
    db = get_database()
    whatsapp = WhatsAppIntegration(db=db)
    return await whatsapp.handle_webhook(request)


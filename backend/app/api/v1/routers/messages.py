"""Messages API router for handling message submissions."""
import os
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class MessageRequest(BaseModel):
    """Message submission request model."""

    content: str = Field(..., min_length=1, max_length=5000, description="Message content")
    locale: Optional[str] = Field(default="en", description="Message locale (ar or en)")


class MessageResponse(BaseModel):
    """Message submission response model."""

    id: str = Field(..., description="Unique message ID")
    content: str = Field(..., description="Message content")
    locale: str = Field(..., description="Message locale")
    delivered: bool = Field(..., description="Whether message was delivered to Telegram")


async def forward_to_telegram(content: str, locale: str) -> bool:
    """
    Forward message to Telegram if bot token and admin chat ID are configured.
    
    Args:
        content: Message content to forward
        locale: Message locale
        
    Returns:
        True if forwarded successfully, False otherwise
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_chat_id = os.getenv("ADMIN_CHAT_ID")
    
    if not bot_token or not admin_chat_id:
        return False
    
    try:
        import httpx
        
        message_text = f"📩 New message [{locale}]:\n\n{content}"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "chat_id": admin_chat_id,
                    "text": message_text,
                    "parse_mode": "HTML"
                },
                timeout=10.0
            )
            return response.status_code == 200
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to forward to Telegram: {e}")
        return False


@router.post("/messages", response_model=MessageResponse)
async def create_message(message: MessageRequest) -> MessageResponse:
    """
    Create a new message and optionally forward to Telegram.
    
    This endpoint accepts messages from the Replies Console and:
    1. Generates a unique ID for the message
    2. Validates the locale (defaults to 'en' if not provided)
    3. Attempts to forward to Telegram if configured
    4. Returns the message details with delivery status
    
    Note: Messages are currently ephemeral (not persisted to database).
    Future versions will add database persistence.
    """
    # Validate locale
    if message.locale not in ["ar", "en"]:
        message.locale = "en"
    
    # Generate unique message ID
    message_id = str(uuid.uuid4())
    
    # Attempt to forward to Telegram
    delivered = await forward_to_telegram(message.content, message.locale)
    
    return MessageResponse(
        id=message_id,
        content=message.content,
        locale=message.locale,
        delivered=delivered
    )


@router.get("/messages/health")
async def messages_health():
    """Health check endpoint for messages service."""
    telegram_configured = bool(
        os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("ADMIN_CHAT_ID")
    )
    
    return {
        "status": "healthy",
        "telegram_configured": telegram_configured,
        "note": "Messages are currently ephemeral. Database persistence coming in future release."
    }

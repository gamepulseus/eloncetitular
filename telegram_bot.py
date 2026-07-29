import logging
import httpx
from typing import Optional
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID

logger = logging.getLogger("TelegramBot")

class TelegramBroadcaster:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.channel_id = TELEGRAM_CHANNEL_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(self, message: str) -> bool:
        """Send HTML formatted message to Telegram channel (@ElOnceTitular)."""
        if not self.bot_token or not self.channel_id or self.channel_id == "@YOUR_CHANNEL_USERNAME":
            logger.warning("Telegram Bot Token or Channel ID not configured. Message preview:")
            logger.info(f"\n--- [TELEGRAM PREVIEW] ---\n{message}\n----------------------------------")
            return False

        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": self.channel_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    logger.info(f"TelegramBot: Successfully posted message to Telegram channel ({self.channel_id}).")
                    return True
                else:
                    logger.error(f"Telegram API returned error: {resp.text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending message to Telegram: {e}")
            return False

    async def send_photo(self, photo_url: str, caption: str, parse_mode: str = "HTML") -> bool:
        """Send a photo with caption to the configured Telegram channel."""
        if not self.bot_token or not self.channel_id:
            return False

        url = f"{self.api_url}/sendPhoto"
        payload = {
            "chat_id": self.channel_id,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": parse_mode
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload)
                return resp.status_code == 200
        except Exception as e:
            logger.error(f"Error sending photo to Telegram: {e}")
            return False

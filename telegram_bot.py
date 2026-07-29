import logging
import httpx
from typing import Optional
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID

logger = logging.getLogger("TelegramBot")

class TelegramBroadcaster:
    def __init__(self, bot_token: str = TELEGRAM_BOT_TOKEN, channel_id: str = TELEGRAM_CHANNEL_ID):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(self, text: str, parse_mode: str = "HTML", disable_preview: bool = True) -> bool:
        """Send a text message to the configured Telegram channel."""
        if not self.bot_token or self.bot_token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            logger.warning("Telegram Bot Token is not configured. Message suppressed:")
            logger.info(f"\n--- [TELEGRAM MESSAGE PREVIEW] ---\n{text}\n----------------------------------")
            return False

        if not self.channel_id:
            logger.warning("Telegram Channel ID is not configured.")
            return False

        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": self.channel_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_preview
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(url, json=payload)
                data = response.json()
                if data.get("ok"):
                    logger.info(f"Successfully posted message to Telegram channel ({self.channel_id}).")
                    return True
                else:
                    logger.error(f"Telegram API returned error: {data.get('description')}")
                    return False
            except Exception as e:
                logger.error(f"Failed to send Telegram message: {e}")
                return False

    async def send_photo(self, photo_url: str, caption: str, parse_mode: str = "HTML") -> bool:
        """Send a photo with caption to the configured Telegram channel."""
        if not self.bot_token or self.bot_token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            logger.warning("Telegram Bot Token is not configured. Photo message suppressed.")
            return False

        url = f"{self.api_url}/sendPhoto"
        payload = {
            "chat_id": self.channel_id,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": parse_mode
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(url, json=payload)
                data = response.json()
                if data.get("ok"):
                    logger.info(f"Successfully posted photo to Telegram channel.")
                    return True
                else:
                    logger.error(f"Telegram photo error: {data.get('description')}")
                    return False
            except Exception as e:
                logger.error(f"Failed to send Telegram photo: {e}")
                return False

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

    async def send_message(self, message: str, channel_id: Optional[str] = None) -> bool:
        """Send HTML formatted message to specified Telegram channel or default channel."""
        target_channel = channel_id or self.channel_id
        
        if not self.bot_token or not target_channel or target_channel == "@YOUR_CHANNEL_USERNAME":
            logger.warning("Telegram Bot Token or Channel ID not configured. Message preview:")
            logger.info(f"\n--- [TELEGRAM PREVIEW ({target_channel})] ---\n{message}\n----------------------------------")
            return False

        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": target_channel,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    logger.info(f"TelegramBot: Successfully posted message to Telegram channel ({target_channel}).")
                    return True
                else:
                    logger.error(f"Telegram API returned error: {resp.text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending message to Telegram ({target_channel}): {e}")
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

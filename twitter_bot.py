import logging
from typing import Optional

logger = logging.getLogger("TwitterBot")

class TwitterBroadcaster:
    def __init__(self):
        self.client: Optional[Any] = None
        logger.info("Twitter/X integration is disabled. Telegram-only mode active.")

    async def send_tweet(self, text: str) -> bool:
        """Twitter broadcasting disabled."""
        return False

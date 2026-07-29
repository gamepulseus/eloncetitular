import logging
import re
import html
import time
import tweepy
from typing import Optional
from config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_BEARER_TOKEN
)

logger = logging.getLogger("TwitterBot")

class TwitterBroadcaster:
    def __init__(self):
        self.client: Optional[tweepy.Client] = None
        self._init_client()

    def _init_client(self):
        if (
            TWITTER_API_KEY and TWITTER_API_KEY != "YOUR_TWITTER_API_KEY" and
            TWITTER_ACCESS_TOKEN and TWITTER_ACCESS_TOKEN != "YOUR_TWITTER_ACCESS_TOKEN"
        ):
            try:
                # Use OAuth 1.0a User Context to consume account credits balance ($5)
                self.client = tweepy.Client(
                    consumer_key=TWITTER_API_KEY,
                    consumer_secret=TWITTER_API_SECRET,
                    access_token=TWITTER_ACCESS_TOKEN,
                    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
                )
                logger.info("Twitter/X User Context Client successfully initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {e}")
                self.client = None
        else:
            logger.info("Twitter/X credentials not configured. Tweets will be logged in dry-run mode.")
            self.client = None

    def clean_html_for_twitter(self, text: str) -> str:
        """Strip HTML tags and unescape entities for Twitter format."""
        clean = html.unescape(text)
        clean = re.sub(r'<[^>]+>', '', clean)
        clean = re.sub(r'\n{3,}', '\n\n', clean)
        return clean.strip()

    def format_tweet_text(self, text: str, max_length: int = 280) -> str:
        """Ensure tweet fits within max_length characters and add unique timestamp to prevent 403 Duplicate Content."""
        clean_text = self.clean_html_for_twitter(text)
        
        # Unique timestamp suffix to prevent Twitter duplicate content 403 errors
        time_tag = f" ⏱️ {time.strftime('%H:%M:%S')}"
        effective_max = max_length - len(time_tag)

        if len(clean_text) <= effective_max:
            return clean_text + time_tag

        # Truncate and add ellipsis + timestamp
        truncated = clean_text[:effective_max - 4] + "..."
        return truncated + time_tag

    async def send_tweet(self, text: str) -> bool:
        """Post a tweet to Twitter / X asynchronously."""
        tweet_text = self.format_tweet_text(text)

        if not self.client:
            logger.warning("Twitter/X Client is not active. Tweet output preview:")
            logger.info(f"\n--- [TWITTER TWEET PREVIEW ({len(tweet_text)} chars)] ---\n{tweet_text}\n----------------------------------")
            return False

        try:
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.client.create_tweet(text=tweet_text)
            )
            if response and response.data:
                logger.info(f"Successfully posted tweet! Tweet ID: {response.data.get('id')}")
                return True
            return False
        except tweepy.errors.HTTPException as e:
            err_msg = str(e).lower()
            if e.response.status_code == 402 or "credits depleted" in err_msg:
                logger.warning("Twitter API: Credits Depleted / Payment Required.")
            elif "duplicate content" in err_msg:
                logger.warning("Twitter API: Duplicate Tweet content suppressed.")
            elif "not permitted" in err_msg or e.response.status_code == 403:
                logger.warning(
                    "Twitter API Limit: Has alcanzado el límite diario de tweets (50 tweets/día en el plan Gratuito de X). "
                    "El límite se reiniciará automáticamente mañana."
                )
            else:
                logger.error(f"Twitter API error ({e.response.status_code}): {e}")
            return False
        except Exception as e:
            logger.error(f"Error posting tweet to Twitter/X: {e}")
            return False

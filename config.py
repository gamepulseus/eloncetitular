import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

STATE_FILE = DATA_DIR / "state.json"

# API-Football
API_KEY = os.getenv("API_FOOTBALL_KEY", "")
API_BASE_URL = os.getenv("API_FOOTBALL_BASE_URL", "https://v3.football.api-sports.io")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")

# Twitter / X Credentials (Disabled)
TWITTER_API_KEY = ""
TWITTER_API_SECRET = ""
TWITTER_ACCESS_TOKEN = ""
TWITTER_ACCESS_TOKEN_SECRET = ""
TWITTER_BEARER_TOKEN = ""

# Polling intervals in seconds
LIVE_POLL_INTERVAL = int(os.getenv("LIVE_POLL_INTERVAL", "60"))
INJURIES_POLL_INTERVAL = int(os.getenv("INJURIES_POLL_INTERVAL", "1800"))
TRANSFERS_POLL_INTERVAL = int(os.getenv("TRANSFERS_POLL_INTERVAL", "3600"))

# Target leagues filter
_leagues_str = os.getenv("TARGET_LEAGUES", "").strip()
TARGET_LEAGUES = [int(l.strip()) for l in _leagues_str.split(",") if l.strip().isdigit()]

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

# Telegram Channel IDs
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@ElOnceTitular")
TELEGRAM_LIVE_CHANNEL_ID = os.getenv("TELEGRAM_LIVE_CHANNEL_ID", "@ElOnceTitular")
TELEGRAM_NEWS_CHANNEL_ID = os.getenv("TELEGRAM_NEWS_CHANNEL_ID", "@ElOnceTitularNoticias")

# Twitter / X Credentials (Disabled)
TWITTER_API_KEY = ""
TWITTER_API_SECRET = ""
TWITTER_ACCESS_TOKEN = ""
TWITTER_ACCESS_TOKEN_SECRET = ""
TWITTER_BEARER_TOKEN = ""

# AI & News Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
NEWS_POLL_INTERVAL = int(os.getenv("NEWS_POLL_INTERVAL", "1800"))

# Polling intervals in seconds
LIVE_POLL_INTERVAL = int(os.getenv("LIVE_POLL_INTERVAL", "10"))
INJURIES_POLL_INTERVAL = int(os.getenv("INJURIES_POLL_INTERVAL", "1800"))
TRANSFERS_POLL_INTERVAL = int(os.getenv("TRANSFERS_POLL_INTERVAL", "3600"))

# List of target league IDs to monitor (includes major leagues, international cups, and national cups)
# Premier, LaLiga, Serie A, Bundesliga, Ligue 1, UCL, UEL, UECL, Arg, Bra, MX, MLS, Saudi, Lib, Sud, FUTVE, Copa Ven, Copa del Rey, Coppa Italia, FA Cup, Carabao, DFB Pokal, Coupe de France, Copa Arg, Copa do Brasil
DEFAULT_TARGET_LEAGUES = "39,140,135,78,61,2,3,848,128,71,262,253,307,13,11,299,1113,137,136,45,48,81,66,130,73"

target_leagues_str = os.getenv("TARGET_LEAGUES", DEFAULT_TARGET_LEAGUES)
TARGET_LEAGUES = [int(x.strip()) for x in target_leagues_str.split(",") if x.strip().isdigit()]

import os
from dotenv import load_dotenv

load_dotenv()

# Environment & Debug
ENV = os.getenv("ENV", "production")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
STATE_FILE = os.getenv("STATE_FILE", "state.json")

# API-Football Credentials
API_KEY = os.getenv("API_FOOTBALL_KEY", "")
API_BASE_URL = os.getenv("API_FOOTBALL_BASE_URL", "https://v3.football.api-sports.io")

# Telegram Channel ID (Live Minute-by-Minute Channel)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@ElOnceTitular")

# Twitter / X Credentials (Disabled)
TWITTER_API_KEY = ""
TWITTER_API_SECRET = ""
TWITTER_ACCESS_TOKEN = ""
TWITTER_ACCESS_TOKEN_SECRET = ""
TWITTER_BEARER_TOKEN = ""

# Polling intervals in seconds (Smart Adaptive Polling to guarantee zero quota exhaustion)
LIVE_POLL_INTERVAL = int(os.getenv("LIVE_POLL_INTERVAL", "15"))  # 15s when matches are live
IDLE_POLL_INTERVAL = int(os.getenv("IDLE_POLL_INTERVAL", "60"))  # 60s when no matches are live

# List of target league IDs to monitor (includes major leagues, international cups, and national cups)
# Premier, LaLiga, Serie A, Bundesliga, Ligue 1, UCL, UEL, UECL, Arg, Bra, MX, MLS, Saudi, Lib, Sud, FUTVE, Copa Ven, Copa del Rey, Coppa Italia, FA Cup, Carabao, DFB Pokal, Coupe de France, Copa Arg, Copa do Brasil
DEFAULT_TARGET_LEAGUES = "39,140,135,78,61,2,3,848,128,71,262,253,307,13,11,299,1113,137,136,45,48,81,66,130,73"

target_leagues_str = os.getenv("TARGET_LEAGUES", DEFAULT_TARGET_LEAGUES)
TARGET_LEAGUES = [int(x.strip()) for x in target_leagues_str.split(",") if x.strip().isdigit()]

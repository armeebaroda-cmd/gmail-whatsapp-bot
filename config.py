"""
config.py — All configuration for Gmail Telegram Summary Bot
Values are read from environment variables (set as GitHub Secrets in production).
For local testing, set these in your shell before running main.py.
"""
import os

# ─── Gmail ────────────────────────────────────────────────────────────────────
GMAIL_ADDRESS       = os.environ.get("GMAIL_ADDRESS", "jignesh.patel@armeeinfotech.com")
GMAIL_APP_PASSWORD  = os.environ.get("GMAIL_APP_PASSWORD", "")   # Gmail App Password
GMAIL_IMAP_HOST     = "imap.gmail.com"
GMAIL_IMAP_PORT     = 993
GMAIL_SMTP_HOST     = "smtp.gmail.com"
GMAIL_SMTP_PORT     = 465

# ─── Telegram Bot ─────────────────────────────────────────────────────────────
# How to get these — see HOW_TO_RUN.md Step 0
TELEGRAM_BOT_TOKEN  = os.environ.get("TELEGRAM_BOT_TOKEN", "")   # From @BotFather
TELEGRAM_CHAT_ID    = os.environ.get("TELEGRAM_CHAT_ID",  "")    # Your Telegram user ID

# ─── Legacy / Unused ──────────────────────────────────────────────────────────
WHATSAPP_PHONE      = os.environ.get("WHATSAPP_PHONE", "+919327189050")
CALLMEBOT_API_KEY   = os.environ.get("CALLMEBOT_API_KEY", "")

# ─── Bot Behaviour ─────────────────────────────────────────────────────────────
SUMMARY_INTERVAL_MINUTES = 60    # How far back to look for emails each run
MAX_EMAILS_PER_SECTION   = 5     # Max emails shown per priority section
MAX_SUBJECT_LEN          = 60    # Truncate long subjects in WA message
MAX_ACTION_LEN           = 110   # Truncate action text in WA message

# ─── File Paths ────────────────────────────────────────────────────────────────
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

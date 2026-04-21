"""
notification_sender.py — Message formatters for both Telegram and WhatsApp.
The bot now uses Telegram by default (free, no country restrictions).
WhatsApp/CallMeBot kept here as legacy fallback.
"""
import urllib.parse
import requests
import time

from config import (
    WHATSAPP_PHONE,
    CALLMEBOT_API_KEY,
    MAX_EMAILS_PER_SECTION,
    MAX_SUBJECT_LEN,
    MAX_ACTION_LEN,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)

CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"
WA_MAX_CHARS  = 4000


# ─── Message Formatter ────────────────────────────────────────────────────────

def format_whatsapp_message(summaries: list, from_time: str, to_time: str) -> str:
    """
    Build the formatted WhatsApp summary string.
    Uses WhatsApp's supported markdown: *bold*, _italic_.
    """
    urgent = [s for s in summaries if s["priority"] == "URGENT"]
    action = [s for s in summaries if s["priority"] == "ACTION"]
    info   = [s for s in summaries if s["priority"] == "INFO"]

    lines = []

    # ── Header ──────────────────────────────────────────────────
    lines.append("📧 *GMAIL HOURLY SUMMARY*")
    lines.append(f"🕐 {from_time} – {to_time}  |  {len(summaries)} New Email{'s' if len(summaries) != 1 else ''}")
    lines.append("")

    def _trunc(text: str, limit: int) -> str:
        return text[:limit] + "…" if len(text) > limit else text

    def add_section(emoji: str, title: str, items: list, max_show: int):
        if not items:
            return
        lines.append(f"{'━' * 22}")
        lines.append(f"{emoji} *{title}* ({len(items)})")
        lines.append(f"{'━' * 22}")
        for em in items[:max_show]:
            subj   = _trunc(em["subject"],     MAX_SUBJECT_LEN)
            action = _trunc(em["action_text"], MAX_ACTION_LEN)
            lines.append(f"*{em['index']}.* {em['from_name']}")
            lines.append(f"   📌 {subj}")
            lines.append(f"   ↳ {action}")
            lines.append("")
        if len(items) > max_show:
            lines.append(f"   _...and {len(items) - max_show} more {title.lower()} email(s)._")
            lines.append("")

    add_section("🔴", "URGENT – Reply Needed", urgent, MAX_EMAILS_PER_SECTION)
    add_section("🟡", "ACTION NEEDED",          action, MAX_EMAILS_PER_SECTION)
    add_section("🟢", "INFO ONLY",              info,   3)

    # ── Reply instructions ────────────────────────────────────────
    lines.append(f"{'━' * 22}")
    lines.append("💬 *To reply to an email:*")
    lines.append("Send yourself an email:")
    lines.append("  Subject:  BOT-REPLY-[number]")
    lines.append("  Body:     Your reply message")

    full_message = "\n".join(lines)

    # Truncate if somehow too long (shouldn't happen for ≤25 emails)
    if len(full_message) > WA_MAX_CHARS:
        full_message = full_message[:WA_MAX_CHARS - 50] + "\n\n_[message truncated]_"

    return full_message


# ─── Sender ───────────────────────────────────────────────────────────────────

def send_whatsapp(message: str, phone: str = None, apikey: str = None) -> bool:
    """
    Send a WhatsApp message via CallMeBot API.
    Returns True on success, False on failure.
    """
    phone  = (phone  or WHATSAPP_PHONE).replace(" ", "").replace("-", "")
    apikey = apikey  or CALLMEBOT_API_KEY

    if not phone:
        print("  [WA ERROR] WHATSAPP_PHONE is not configured.")
        return False
    if not apikey:
        print("  [WA ERROR] CALLMEBOT_API_KEY is not configured. "
              "Run CallMeBot activation first (see setup_guide.md).")
        return False

    # URL-encode the message text
    encoded = urllib.parse.quote(message)
    url = f"{CALLMEBOT_URL}?phone={phone}&text={encoded}&apikey={apikey}"

    for attempt in range(1, 4):   # up to 3 attempts
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                print(f"  [WA] ✅ Message sent to {phone} (attempt {attempt})")
                return True
            else:
                print(f"  [WA] Attempt {attempt}: HTTP {resp.status_code} – {resp.text[:200]}")
        except requests.exceptions.Timeout:
            print(f"  [WA] Attempt {attempt}: request timed out.")
        except Exception as e:
            print(f"  [WA] Attempt {attempt}: {e}")

        if attempt < 3:
            time.sleep(5)   # wait before retry

    print("  [WA] ❌ All 3 attempts failed.")
    return False

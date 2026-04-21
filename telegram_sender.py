"""
telegram_sender.py — Sends messages via Telegram Bot API (FREE, no restrictions).
Replaces CallMeBot which is not available in India.

Setup (2 minutes):
  1. Open Telegram app → search for @BotFather
  2. Send: /newbot
  3. Give your bot a name (e.g. "Gmail Summary Bot")
  4. Give a username (e.g. "my_gmail_summary_bot")
  5. BotFather replies with your TOKEN — save it
  6. Now search for your bot name in Telegram and click START
  7. Open: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
  8. Copy the "id" number from "chat" — that is your CHAT_ID
  9. Save TOKEN and CHAT_ID as GitHub Secrets
"""
import urllib.parse
import requests
import time

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
TG_MAX_CHARS = 4000   # Telegram max per message is 4096


def _split_long_message(text: str, limit: int = TG_MAX_CHARS) -> list:
    """Split a long message into chunks that fit within Telegram's limit."""
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        # Find last newline before limit
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


def send_telegram(message: str, token: str = None, chat_id: str = None) -> bool:
    """
    Send a message via Telegram Bot API.
    Uses HTML parse mode for formatting (<b>, <i>, etc.)
    Returns True on success, False on failure.
    """
    token   = token   or TELEGRAM_BOT_TOKEN
    chat_id = chat_id or TELEGRAM_CHAT_ID

    if not token:
        print("  [TG ERROR] TELEGRAM_BOT_TOKEN is not configured.")
        return False
    if not chat_id:
        print("  [TG ERROR] TELEGRAM_CHAT_ID is not configured.")
        return False

    url    = TELEGRAM_API.format(token=token)
    chunks = _split_long_message(message)

    all_ok = True
    for i, chunk in enumerate(chunks, start=1):
        payload = {
            "chat_id":    chat_id,
            "text":       chunk,
            "parse_mode": "HTML",
        }
        for attempt in range(1, 4):
            try:
                resp = requests.post(url, json=payload, timeout=30)
                if resp.status_code == 200 and resp.json().get("ok"):
                    print(f"  [TG] ✅ Message part {i}/{len(chunks)} sent (attempt {attempt})")
                    break
                else:
                    err = resp.json().get("description", resp.text[:100])
                    print(f"  [TG] Attempt {attempt}: Error — {err}")
            except requests.exceptions.Timeout:
                print(f"  [TG] Attempt {attempt}: Timed out.")
            except Exception as e:
                print(f"  [TG] Attempt {attempt}: {e}")

            if attempt < 3:
                time.sleep(3)
        else:
            all_ok = False

        if len(chunks) > 1:
            time.sleep(1)  # small delay between chunks

    return all_ok

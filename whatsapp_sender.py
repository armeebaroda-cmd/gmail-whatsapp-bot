"""
whatsapp_sender.py — Telegram HTML message formatter for Gmail Summary Bot.
Formats emails into clean, well-aligned Telegram messages using HTML parse mode.
"""
import time
import requests

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    MAX_EMAILS_PER_SECTION,
)

TG_MAX_CHARS = 4000


# ─── HTML Helpers ─────────────────────────────────────────────────────────────

def _b(text: str) -> str:
    """Bold text in Telegram HTML."""
    return f"<b>{_esc(text)}</b>"

def _i(text: str) -> str:
    """Italic text in Telegram HTML."""
    return f"<i>{_esc(text)}</i>"

def _esc(text: str) -> str:
    """Escape HTML special characters for Telegram."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _trunc(text: str, limit: int) -> str:
    """Truncate long text with ellipsis."""
    text = str(text).strip()
    return text[:limit] + "…" if len(text) > limit else text


# ─── Email Number Badges ──────────────────────────────────────────────────────

EMOJI_NUMS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]

def _num(n: int) -> str:
    return EMOJI_NUMS[n - 1] if 1 <= n <= 10 else f"{n}."


# ─── Message Formatter ────────────────────────────────────────────────────────

def format_whatsapp_message(summaries: list, from_time: str, to_time: str) -> str:
    """
    Build a clean, aligned Gmail summary message in Telegram HTML format.

    Layout example:
    ┌──────────────────────────────────┐
    │ 📧 GMAIL SUMMARY                 │
    │ 🕐 02:30 PM → 03:30 PM | 12 mails│
    │ 🔴 3  🟡 6  🟢 3                 │
    │                                  │
    │ 🔴 URGENT — Reply Needed (3)     │
    │ ──────────────────────────────── │
    │ 1️⃣  Jinal Ranapariya             │
    │    📌 OEM Ticket Escalation       │
    │    ↳ Customer needs reply ASAP   │
    │                                  │
    │ 🟡 ACTION NEEDED (6)             │
    │ ...                              │
    │                                  │
    │ 💬 HOW TO REPLY                  │
    │ To reply to email 1️⃣:            │
    │ • Open Gmail → Compose new email │
    │ • To: jignesh.patel@armeeinf...  │
    │ • Subject: BOT-REPLY-1           │
    │ • Body: your reply message       │
    └──────────────────────────────────┘
    """
    urgent = [s for s in summaries if s["priority"] == "URGENT"]
    action = [s for s in summaries if s["priority"] == "ACTION"]
    info   = [s for s in summaries if s["priority"] == "INFO"]

    lines = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines.append("📧 " + _b("GMAIL HOURLY SUMMARY"))
    lines.append(f"🕐 {_b(from_time)}  →  {_b(to_time)}")
    lines.append(
        f"📊 Total: {_b(str(len(summaries)))} emails"
        f"  |  🔴 {_b(str(len(urgent)))}"
        f"  🟡 {_b(str(len(action)))}"
        f"  🟢 {_b(str(len(info)))}"
    )
    lines.append("")

    # ── Section builder ───────────────────────────────────────────────────────
    def add_section(emoji: str, title: str, items: list, max_show: int):
        if not items:
            return
        lines.append(f"{emoji} {_b(f'{title}  ({len(items)})')}")
        lines.append("─" * 32)
        for em in items[:max_show]:
            idx    = em["index"]
            name   = _trunc(em["from_name"],   30)
            subj   = _trunc(em["subject"],      55)
            action = _trunc(em["action_text"], 110)
            lines.append(f"{_num(idx)}  {_b(name)}")
            lines.append(f"    📌 {_esc(subj)}")
            lines.append(f"    ↳ {_i(action)}")
            lines.append("")
        if len(items) > max_show:
            remaining = len(items) - max_show
            lines.append(_i(f"    ... and {remaining} more {title.lower()} email(s)"))
            lines.append("")

    add_section("🔴", "URGENT — Reply Needed", urgent, MAX_EMAILS_PER_SECTION)
    add_section("🟡", "ACTION NEEDED",          action, MAX_EMAILS_PER_SECTION)
    add_section("🟢", "INFO ONLY",              info,   3)

    # ── Reply Instructions ────────────────────────────────────────────────────
    lines.append("─" * 32)
    lines.append("💬 " + _b("HOW TO REPLY TO AN EMAIL"))
    lines.append("")
    lines.append("Suppose you want to reply to email " + _b("1️⃣") + ":")
    lines.append("")
    lines.append("  1. Open " + _b("Gmail") + " on your phone")
    lines.append("  2. Tap " + _b("✏️ Compose") + " (new email)")
    lines.append("  3. " + _b("To:") + "  yourself  " + _i("(jignesh.patel@armeeinfotech.com)"))
    lines.append("  4. " + _b("Subject:") + "  <code>BOT-REPLY-1</code>")
    lines.append("     " + _i("(change 1 to the email number you want)"))
    lines.append("  5. " + _b("Body:") + "  write your reply message")
    lines.append("  6. " + _b("Send") + " — bot sends your reply next hour ✅")
    lines.append("")
    lines.append(_i("Example: to reply to email 3️⃣, use Subject: BOT-REPLY-3"))

    full_message = "\n".join(lines)

    # Split if too long (Telegram limit ~4096)
    if len(full_message) > TG_MAX_CHARS:
        full_message = full_message[:TG_MAX_CHARS - 80] + "\n\n" + _i("[message truncated — too many emails]")

    return full_message


def format_no_emails_message(from_time: str, to_time: str) -> str:
    """Message sent when there are no new emails this hour."""
    lines = [
        "📧 " + _b("GMAIL HOURLY SUMMARY"),
        f"🕐 {_b(from_time)}  →  {_b(to_time)}",
        "",
        "✅ " + _b("No new emails this hour."),
        _i("Bot is running normally. Next check in 1 hour."),
    ]
    return "\n".join(lines)


# ─── Legacy WhatsApp sender (unused, kept for reference) ─────────────────────

def send_whatsapp(message: str) -> bool:
    """Not used — bot uses Telegram. Kept to avoid import errors."""
    print("  [WA] send_whatsapp() called but Telegram is used instead.")
    from telegram_sender import send_telegram
    return send_telegram(message)

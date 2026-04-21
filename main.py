#!/usr/bin/env python3
"""
main.py — Gmail Telegram Hourly Summary Bot
============================================
Entry point called by GitHub Actions every hour.
Can also be run manually for testing:

  python main.py                   → full run
  python main.py --once            → alias for full run
  python main.py --test-gmail      → test Gmail IMAP only
  python main.py --test-telegram   → send a test Telegram message
"""

import sys
import os
import datetime
import traceback

from config import GMAIL_ADDRESS, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


# ─── Helpers ─────────────────────────────────────────────────────────────────

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

def _fmt_ist(dt: datetime.datetime) -> str:
    """Format a UTC datetime as IST time string, e.g. '02:30 PM'."""
    return dt.astimezone(IST).strftime("%I:%M %p")

def _separator(title: str = ""):
    bar = "=" * 60
    print(bar)
    if title:
        print(f"  {title}")
        print(bar)


# ─── Preflight Checks ─────────────────────────────────────────────────────────

def _check_config() -> bool:
    errors = []
    if not GMAIL_ADDRESS:
        errors.append("GMAIL_ADDRESS is not set")
    if not os.environ.get("GMAIL_APP_PASSWORD"):
        errors.append("GMAIL_APP_PASSWORD is not set")
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is not set (get it from @BotFather on Telegram)")
    if not TELEGRAM_CHAT_ID:
        errors.append("TELEGRAM_CHAT_ID is not set (see HOW_TO_RUN.md Step 0)")

    if errors:
        print("❌ Configuration errors (set these as GitHub Secrets or env vars):")
        for e in errors:
            print(f"   • {e}")
        return False
    return True


# ─── Main Run ─────────────────────────────────────────────────────────────────

def run():
    """Execute one full bot cycle."""
    from state_manager    import load_state, save_state, get_since_datetime
    from gmail_reader     import fetch_emails
    from email_summarizer import summarize_emails
    from whatsapp_sender  import format_whatsapp_message
    from telegram_sender  import send_telegram
    from reply_handler    import check_and_process_replies

    now_utc = datetime.datetime.now(datetime.timezone.utc)

    _separator("Gmail Telegram Summary Bot — Starting")
    print(f"  Run time (IST)    : {_fmt_ist(now_utc)}")
    print(f"  Gmail account     : {GMAIL_ADDRESS}")
    print(f"  Telegram chat ID  : {TELEGRAM_CHAT_ID}")

    # ── 1. Config Check ───────────────────────────────────────────────────────
    if not _check_config():
        sys.exit(1)

    # ── 2. Load State ─────────────────────────────────────────────────────────
    _separator("1 / 5  Load State")
    state    = load_state()
    since_dt = get_since_datetime(state)
    print(f"  Fetching emails since: {_fmt_ist(since_dt)} IST")

    # ── 3. Process Pending Replies ────────────────────────────────────────────
    _separator("2 / 5  Process Pending Replies")
    pending = state.get("pending_emails", [])
    if pending:
        print(f"  {len(pending)} pending email(s) in state — checking for BOT-REPLY messages …")
        try:
            reply_results = check_and_process_replies(pending)
            if reply_results:
                print(f"  Sent {len(reply_results)} reply(ies).")
                for r in reply_results:
                    confirm = (
                        f"✅ <b>Reply Sent</b>\n"
                        f"Email #{r['index']}: {r['subject'][:60]}\n"
                        f"To: {r['to']}"
                    )
                    send_telegram(confirm)
            else:
                print("  No BOT-REPLY emails found in inbox.")
        except Exception as e:
            print(f"  [WARN] Reply handler error (non-fatal): {e}")
    else:
        print("  No pending emails in state — skipping reply check.")

    # ── 4. Fetch New Emails ───────────────────────────────────────────────────
    _separator("3 / 5  Fetch New Emails from Gmail")
    try:
        emails = fetch_emails(since_dt)
    except Exception as e:
        print(f"❌ Gmail fetch failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # Update timestamp immediately (even if no emails, so next run is accurate)
    state["last_processed"] = now_utc.isoformat()

    if not emails:
        print(f"  No new emails since {_fmt_ist(since_dt)} IST.")
        save_state(state)
        _separator("Done — No emails to report.")
        return

    print(f"  {len(emails)} new email(s) found.")

    # ── 5. Summarise & Classify ───────────────────────────────────────────────
    _separator("4 / 5  Summarise & Classify")
    summaries    = summarize_emails(emails)
    urgent_count = sum(1 for s in summaries if s["priority"] == "URGENT")
    action_count = sum(1 for s in summaries if s["priority"] == "ACTION")
    info_count   = sum(1 for s in summaries if s["priority"] == "INFO")
    print(f"  🔴 Urgent: {urgent_count}   🟡 Action: {action_count}   🟢 Info: {info_count}")

    # Store summaries in state for reply mapping on next run
    state["pending_emails"] = summaries

    # ── 6. Build & Send Telegram Message ────────────────────────────────────
    _separator("5 / 5  Send Telegram Summary")
    from_time = _fmt_ist(since_dt)
    to_time   = _fmt_ist(now_utc)

    message = format_whatsapp_message(summaries, from_time, to_time)

    print("\n┌── Telegram Message Preview ───────────────────────┐")
    for line in message.splitlines()[:20]:
        print(f"│ {line}")
    if message.count("\n") > 20:
        print("│ … [truncated for preview] …")
    print("└───────────────────────────────────────────────────┘\n")

    success = send_telegram(message)

    # ── 7. Save State ─────────────────────────────────────────────────────────
    save_state(state)

    _separator("Bot Run Complete")
    if success:
        print("✅ Telegram message sent successfully!")
    else:
        print("⚠️  Telegram send failed — check TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.")
    print("")


# ─── Test Modes ───────────────────────────────────────────────────────────────

def test_gmail():
    """Verify Gmail IMAP credentials and connectivity."""
    _separator("TEST: Gmail IMAP Connection")
    from gmail_reader import fetch_emails
    since = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
    try:
        emails = fetch_emails(since)
        print(f"\n✅ Gmail connected! Found {len(emails)} email(s) in the last hour.")
        for em in emails[:3]:
            print(f"   • [{em['date'][:16]}] From: {em['from'][:50]} | {em['subject'][:50]}")
    except Exception as e:
        print(f"\n❌ Gmail test failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def test_telegram():
    """Send a test Telegram message to verify bot setup."""
    _separator("TEST: Telegram Bot")
    from telegram_sender import send_telegram
    msg = (
        "🤖 <b>Gmail Bot — Test Message</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "✅ Telegram setup is working correctly!\n"
        "You will receive Gmail summaries every hour."
    )
    success = send_telegram(msg)
    if success:
        print("\n✅ Test Telegram message sent! Check your Telegram app.")
    else:
        print("\n❌ Telegram test failed. Check TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.")
        sys.exit(1)


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    if "--test-gmail" in args:
        test_gmail()
    elif "--test-telegram" in args:
        test_telegram()
    elif "--once" in args or not args:
        run()
    else:
        print("Usage:")
        print("  python main.py                   → full hourly run")
        print("  python main.py --once            → same as above")
        print("  python main.py --test-gmail      → test Gmail connection")
        print("  python main.py --test-telegram   → send a test Telegram message")

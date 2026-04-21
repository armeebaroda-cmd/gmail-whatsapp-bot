"""
state_manager.py — Persists the bot's last-run state in state.json.
GitHub Actions commits state.json back to the repo after every run,
so the next run knows exactly where it left off.
"""
import json
import os
from datetime import datetime, timezone, timedelta
from config import STATE_FILE, SUMMARY_INTERVAL_MINUTES

DEFAULT_STATE = {
    "last_processed": None,       # ISO-format UTC datetime string
    "pending_emails":  [],        # List of summarised emails (for BOT-REPLY handling)
}


def load_state() -> dict:
    """Load state from state.json. Returns default if file is missing or corrupt."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            # Merge with defaults so missing keys don't crash anything
            return {**DEFAULT_STATE, **saved}
        except Exception as e:
            print(f"  [STATE] Could not read state.json ({e}), using defaults.")
    return DEFAULT_STATE.copy()


def save_state(state: dict) -> None:
    """Write state to state.json (committed back to repo by GitHub Actions)."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, default=str)
    print(f"  [STATE] Saved → {STATE_FILE}")


def get_since_datetime(state: dict) -> datetime:
    """
    Return the UTC datetime from which to fetch new emails.
    - If state has a valid last_processed timestamp → use that.
    - Otherwise → go back SUMMARY_INTERVAL_MINUTES minutes from now.
    """
    last = state.get("last_processed")
    if last:
        try:
            dt = datetime.fromisoformat(last)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            pass
    fallback = datetime.now(timezone.utc) - timedelta(minutes=SUMMARY_INTERVAL_MINUTES)
    print(f"  [STATE] No previous timestamp – falling back to last {SUMMARY_INTERVAL_MINUTES} min.")
    return fallback

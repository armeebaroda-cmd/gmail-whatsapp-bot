"""
gmail_reader.py — Connects to Gmail via IMAP and fetches emails since a given datetime.
Uses only Python's built-in libraries (imaplib, email) — no third-party packages needed.
"""
import imaplib
import email
import email.header
import html.parser
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, GMAIL_IMAP_HOST, GMAIL_IMAP_PORT
import time


# ─── HTML Stripper ─────────────────────────────────────────────────────────────

class _HTMLStripper(html.parser.HTMLParser):
    """Strips HTML tags and returns plain text."""
    SKIP_TAGS = {"script", "style", "head", "meta", "link"}

    def __init__(self):
        super().__init__()
        self._parts = []
        self._skip  = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.SKIP_TAGS:
            self._skip = True

    def handle_endtag(self, tag):
        if tag.lower() in self.SKIP_TAGS:
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self._parts.append(data)

    def get_text(self):
        text = " ".join(self._parts)
        return re.sub(r"\s+", " ", text).strip()


def _strip_html(raw_html: str) -> str:
    try:
        s = _HTMLStripper()
        s.feed(raw_html)
        return s.get_text()
    except Exception:
        return re.sub(r"<[^>]+>", " ", raw_html).strip()


# ─── Header Decoder ───────────────────────────────────────────────────────────

def _decode_header(value: str) -> str:
    if not value:
        return ""
    parts = []
    for chunk, charset in email.header.decode_header(value):
        if isinstance(chunk, bytes):
            try:
                parts.append(chunk.decode(charset or "utf-8", errors="replace"))
            except (LookupError, TypeError):
                parts.append(chunk.decode("utf-8", errors="replace"))
        else:
            parts.append(chunk)
    return " ".join(parts).strip()


# ─── Body Extractor ───────────────────────────────────────────────────────────

def _get_body(msg) -> str:
    """Extract the best plain-text body from a Message object."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct   = part.get_content_type()
            disp = str(part.get("Content-Disposition", ""))
            if "attachment" in disp:
                continue
            if ct == "text/plain":
                try:
                    charset = part.get_content_charset() or "utf-8"
                    body = part.get_payload(decode=True).decode(charset, errors="replace")
                    break   # prefer plain text; stop searching
                except Exception:
                    continue
            elif ct == "text/html" and not body:
                try:
                    charset = part.get_content_charset() or "utf-8"
                    body = _strip_html(part.get_payload(decode=True).decode(charset, errors="replace"))
                except Exception:
                    continue
    else:
        try:
            charset = msg.get_content_charset() or "utf-8"
            payload = msg.get_payload(decode=True)
            if payload:
                raw = payload.decode(charset, errors="replace")
                body = _strip_html(raw) if msg.get_content_type() == "text/html" else raw
        except Exception:
            body = str(msg.get_payload())

    return body.strip()


# ─── Main Fetcher ─────────────────────────────────────────────────────────────

def fetch_emails(since_dt: datetime) -> list:
    """
    Connect to Gmail IMAP and return a list of email dicts for messages
    received AFTER since_dt.

    Each dict contains:
        uid, message_id, from, subject, date (ISO), body_preview, reply_to, raw_body
    """
    emails = []
    print(f"  Connecting to {GMAIL_IMAP_HOST}:{GMAIL_IMAP_PORT} …")

    try:
        # Wrap IMAP connection in a retry loop to prevent random cloud networking hangs
        mail = None
        for attempt in range(1, 4):
            try:
                mail = imaplib.IMAP4_SSL(GMAIL_IMAP_HOST, GMAIL_IMAP_PORT, timeout=30)
                mail.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
                break
            except Exception as e:
                print(f"  [WARN] IMAP connection attempt {attempt} failed: {e}")
                if attempt == 3:
                    raise
                time.sleep(5)
                
        mail.select("INBOX")

        # IMAP SINCE is date-only; we filter by exact time in Python below
        since_date_str = since_dt.strftime("%d-%b-%Y")
        status, data = mail.search(None, f'(SINCE "{since_date_str}")')

        if status != "OK" or not data[0]:
            print("  IMAP search returned no results.")
            mail.logout()
            return []

        message_ids = data[0].split()
        print(f"  IMAP returned {len(message_ids)} candidate(s) on/after {since_date_str}.")

        for msg_id in message_ids:
            try:
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    continue

                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)

                # Parse arrival datetime
                try:
                    msg_dt = parsedate_to_datetime(msg.get("Date", ""))
                    if msg_dt.tzinfo is None:
                        msg_dt = msg_dt.replace(tzinfo=timezone.utc)
                except Exception:
                    msg_dt = datetime.now(timezone.utc)

                # Time-based filter (IMAP SINCE is day granularity only)
                if msg_dt < since_dt:
                    continue

                from_addr  = _decode_header(msg.get("From", ""))
                subject    = _decode_header(msg.get("Subject", "(No Subject)"))
                message_id = msg.get("Message-ID", "").strip()
                reply_to   = _decode_header(msg.get("Reply-To", from_addr))

                body = _get_body(msg)

                emails.append({
                    "uid":          msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id),
                    "message_id":   message_id,
                    "from":         from_addr,
                    "subject":      subject,
                    "date":         msg_dt.isoformat(),
                    "body_preview": body[:300],
                    "raw_body":     body[:600],
                    "reply_to":     reply_to,
                })

            except Exception as e:
                print(f"  [WARN] Error reading email {msg_id}: {e}")
                continue

        mail.logout()

    except imaplib.IMAP4.error as e:
        print(f"  [ERROR] IMAP authentication/connection error: {e}")
        raise
    except Exception as e:
        print(f"  [ERROR] Unexpected IMAP error: {e}")
        raise

    # Sort oldest → newest
    emails.sort(key=lambda x: x.get("date", ""))
    print(f"  Fetched {len(emails)} new email(s) after time filter.")
    return emails

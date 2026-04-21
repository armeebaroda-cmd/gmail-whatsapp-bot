"""
reply_handler.py — Monitors Gmail inbox for BOT-REPLY-N emails.
When you want to reply to email #2 in the summary, simply send an email to
your own Gmail with:
  Subject : BOT-REPLY-2
  Body    : Your actual reply message here

The bot picks this up on the next run and sends the reply to the original sender.
"""
import imaplib
import email
import email.header
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText

from config import (
    GMAIL_ADDRESS,
    GMAIL_APP_PASSWORD,
    GMAIL_IMAP_HOST,
    GMAIL_IMAP_PORT,
    GMAIL_SMTP_HOST,
    GMAIL_SMTP_PORT,
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _decode_header(value: str) -> str:
    if not value:
        return ""
    parts = []
    for chunk, charset in email.header.decode_header(value):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(chunk)
    return " ".join(parts).strip()


def _get_plain_body(msg) -> str:
    """Extract plain-text body from a Message object."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    charset = part.get_content_charset() or "utf-8"
                    return part.get_payload(decode=True).decode(charset, errors="replace")
                except Exception:
                    continue
    else:
        try:
            charset = msg.get_content_charset() or "utf-8"
            payload = msg.get_payload(decode=True)
            if payload:
                return payload.decode(charset, errors="replace")
        except Exception:
            pass
    return ""


# ─── Reply Sender ─────────────────────────────────────────────────────────────

def _send_email_reply(to_addr: str, subject: str, body: str, in_reply_to: str = "") -> bool:
    """Send an email via Gmail SMTP."""
    try:
        msg = MIMEMultipart()
        msg["From"]    = GMAIL_ADDRESS
        msg["To"]      = to_addr
        msg["Subject"] = subject
        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
            msg["References"]  = in_reply_to

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT, timeout=30) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_addr, msg.as_string())

        print(f"    ✅ Email reply sent to: {to_addr}")
        return True

    except Exception as e:
        print(f"    ❌ SMTP send error: {e}")
        return False


# ─── Main Handler ─────────────────────────────────────────────────────────────

def check_and_process_replies(pending_emails: list) -> list:
    """
    Scan Gmail INBOX for emails with subject matching 'BOT-REPLY-N'.
    For each found:
      1. Look up email #N in pending_emails state.
      2. Send the body as a reply to the original sender.
      3. Mark the BOT-REPLY email as read (so it's not processed again).

    Returns a list of result dicts: {index, to, subject, status}
    """
    results = []

    if not pending_emails:
        return results

    try:
        mail = imaplib.IMAP4_SSL(GMAIL_IMAP_HOST, GMAIL_IMAP_PORT)
        mail.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        mail.select("INBOX")

        # Search for unread BOT-REPLY-N emails (from yourself)
        status, data = mail.search(None, '(UNSEEN SUBJECT "BOT-REPLY-")')
        if status != "OK" or not data[0]:
            print("    No BOT-REPLY emails found.")
            mail.logout()
            return results

        for msg_id in data[0].split():
            try:
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    continue

                msg     = email.message_from_bytes(msg_data[0][1])
                subject = _decode_header(msg.get("Subject", ""))

                # Extract the index number from "BOT-REPLY-3" → 3
                match = re.search(r"BOT-REPLY-(\d+)", subject, re.IGNORECASE)
                if not match:
                    continue

                email_index = int(match.group(1))

                # Find the matching pending email
                target = next(
                    (p for p in pending_emails if p.get("index") == email_index),
                    None
                )
                if not target:
                    print(f"    [REPLY] No pending email #{email_index} in state. Skipping.")
                    continue

                # Get the reply body
                reply_body = _get_plain_body(msg).strip()

                # Remove any auto-added quoted text (lines starting with ">")
                clean_lines = [
                    line for line in reply_body.splitlines()
                    if not line.startswith(">") and not line.lower().startswith("on ")
                ]
                reply_body = "\n".join(clean_lines).strip()

                if not reply_body:
                    print(f"    [REPLY] Empty reply body for BOT-REPLY-{email_index}. Skipping.")
                    continue

                print(f"    [REPLY] Sending reply for email #{email_index} → {target['reply_to']}")

                success = _send_email_reply(
                    to_addr    = target["reply_to"],
                    subject    = f"Re: {target['subject']}",
                    body       = reply_body,
                    in_reply_to= target["message_id"],
                )

                if success:
                    results.append({
                        "index":   email_index,
                        "to":      target["reply_to"],
                        "subject": target["subject"],
                        "status":  "sent",
                    })
                    # Mark BOT-REPLY email as Seen so we don't process it again
                    mail.store(msg_id, "+FLAGS", "\\Seen")

            except Exception as e:
                print(f"    [REPLY] Error processing message {msg_id}: {e}")
                continue

        mail.logout()

    except Exception as e:
        print(f"  [REPLY HANDLER] IMAP error: {e}")

    return results

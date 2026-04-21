"""
email_summarizer.py — Rule-based email classifier and summariser.
No AI API key needed. Uses keyword scoring to classify emails into:
  🔴 URGENT   — needs immediate attention / reply
  🟡 ACTION   — needs action but not urgent
  🟢 INFO     — informational / no action needed
"""
import re

# ─── Keyword Lists ────────────────────────────────────────────────────────────

URGENT_KEYWORDS = [
    "urgent", "asap", "immediately", "immediate", "escalat", "complaint",
    "critical", "emergency", "overdue", "high priority", "time-sensitive",
    "time sensitive", "breach", "legal", "lawsuit", "penalty", "final notice",
    "last chance", "must act", "expires today", "expiring", "suspend",
    "blocked", "terminated", "incident", "outage", "system down", "failed",
    "failure", "error", "alert", "warning", "violation", "fraud", "hack",
    "compromised", "action required", "requires immediate",
]

ACTION_KEYWORDS = [
    "review", "please review", "for your review", "confirm", "please confirm",
    "approval", "approve", "awaiting approval", "invoice", "pending",
    "follow up", "follow-up", "response needed", "deadline", "by tomorrow",
    "end of day", " eod", " cob", "by friday", "by monday", "by today",
    "please check", "please verify", "kindly", "kindly revert",
    "need your", "needs your", "your attention", "please respond",
    "revert back", "revert at", "awaiting", "waiting for your",
    "attached", "attachment", "quote", "proposal", "agreement", "contract",
    "meeting", "interview", "feedback", "report due", "submission",
    "please find", "please send", "require", "request you",
]

LOW_PRIORITY_SENDER_PATTERNS = [
    "noreply", "no-reply", "donotreply", "do-not-reply",
    "newsletter", "marketing", "notifications@", "alerts@",
    "automated", "mailer", "bounce", "postmaster", "info@",
    "support@", "admin@", "digest@",
]

LOW_PRIORITY_SUBJECT_PATTERNS = [
    "unsubscribe", "newsletter", "weekly digest", "daily digest",
    "monthly digest", "promotion", " sale ", "deal ", "offer ",
    "discount", "coupon", "fyi:", "fyi -", "[fyi]", "no action",
    "subscription", "payment received", "order confirmation",
]


# ─── Classification Engine ────────────────────────────────────────────────────

def _is_low_priority_sender(from_addr: str) -> bool:
    fa = from_addr.lower()
    return any(p in fa for p in LOW_PRIORITY_SENDER_PATTERNS)


def _is_low_priority_subject(subject: str) -> bool:
    sub = subject.lower()
    return any(p in sub for p in LOW_PRIORITY_SUBJECT_PATTERNS)


def classify_email(email_dict: dict) -> tuple:
    """
    Returns (priority_str, action_text) where priority_str is
    "URGENT", "ACTION", or "INFO".
    """
    subject  = (email_dict.get("subject")  or "").lower()
    body     = (email_dict.get("raw_body") or "").lower()
    from_fld = (email_dict.get("from")     or "").lower()
    combined = f"{subject} {body}"

    low_sender  = _is_low_priority_sender(from_fld)
    low_subject = _is_low_priority_subject(subject)

    urgent_hits = sum(1 for kw in URGENT_KEYWORDS if kw in combined)
    action_hits = sum(1 for kw in ACTION_KEYWORDS if kw in combined)

    action_text = _extract_action_text(email_dict)

    # Scoring rules
    if not low_sender and urgent_hits >= 1:
        return "URGENT", action_text

    if not low_sender and not low_subject and action_hits >= 1:
        return "ACTION", action_text

    return "INFO", "No action needed."


def _extract_action_text(email_dict: dict) -> str:
    """Return a meaningful one-liner describing what action is needed."""
    body    = (email_dict.get("body_preview") or "").strip()
    subject = (email_dict.get("subject")      or "").strip()

    # Split body into sentences and pick the most meaningful one
    sentences = re.split(r"[.!?\n]", body)
    for s in sentences:
        s = s.strip()
        # Skip very short or whitespace-only sentences
        if len(s) > 25 and not re.match(r"^[\W\s]+$", s):
            # Avoid boilerplate-looking lines
            if not any(bp in s.lower() for bp in ["click here", "unsubscribe",
                                                    "privacy policy", "terms of",
                                                    "view in browser", "confidential"]):
                return s[:120]

    if subject:
        return f"Regarding: {subject[:100]}"
    return "Check email for details."


# ─── Sender Name Extractor ────────────────────────────────────────────────────

def _extract_sender_name(from_field: str) -> str:
    """Extract display name from 'Display Name <email@domain.com>' format."""
    m = re.match(r'^"?([^"<\n]+?)"?\s*<', from_field)
    if m:
        return m.group(1).strip()[:40]
    # Fallback: just use the email address
    m2 = re.match(r"[\w.+%-]+@[\w.-]+", from_field)
    if m2:
        return m2.group(0)[:40]
    return from_field.strip()[:40]


# ─── Public API ───────────────────────────────────────────────────────────────

def summarize_emails(emails: list) -> list:
    """
    Given a list of raw email dicts from gmail_reader.fetch_emails(),
    return a sorted, indexed list of summary dicts ready for formatting.

    Output dict keys:
        index, from, from_name, subject, priority, action_text,
        message_id, reply_to, date, uid
    """
    summaries = []
    for em in emails:
        priority, action_text = classify_email(em)
        summaries.append({
            "index":       0,           # filled in after sort
            "from":        em.get("from", ""),
            "from_name":   _extract_sender_name(em.get("from", "")),
            "subject":     em.get("subject", "(No Subject)"),
            "priority":    priority,
            "action_text": action_text,
            "message_id":  em.get("message_id", ""),
            "reply_to":    em.get("reply_to", em.get("from", "")),
            "date":        em.get("date", ""),
            "uid":         em.get("uid", ""),
        })

    # Sort: URGENT → ACTION → INFO
    order = {"URGENT": 0, "ACTION": 1, "INFO": 2}
    summaries.sort(key=lambda x: order.get(x["priority"], 3))

    # Assign sequential display indices after sort
    for i, s in enumerate(summaries, start=1):
        s["index"] = i

    return summaries

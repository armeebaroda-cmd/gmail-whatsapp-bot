# Gmail WhatsApp Bot — Complete Setup Guide
## Deploy in 15 Minutes — Works Even When PC is Off

---

## STEP 0 — Fix CallMeBot WhatsApp Activation

If you cannot send a WhatsApp to the CallMeBot number, **tap this link from your phone**:

👉 **[Click here to open WhatsApp with pre-filled message](https://wa.me/34644524045?text=I%20allow%20callmebot%20to%20send%20me%20messages)**

Or manually:
1. Open WhatsApp on your phone
2. Tap the **Chat / New Chat** icon (pencil icon, bottom right)
3. Search for the contact you saved as "CallMeBot" (+34 644 52 40 45)
4. Type exactly: `I allow callmebot to send me messages`
5. Send it — they will reply with your **API key** within 1–2 minutes
6. **Save that API key** — you need it in Step 3

> ⚠️ If the contact doesn't appear, open WhatsApp → Settings → New Chat → type the
> number `+34 644 52 40 45` directly in the search bar.

---

## STEP 1 — Enable Gmail IMAP + Create App Password

> Your Gmail account is: **jignesh.patel@armeeinfotech.com**

### 1a. Enable IMAP
1. Open Gmail → Click the **⚙ Settings gear** (top right) → **See all settings**
2. Click **Forwarding and POP/IMAP** tab
3. Under **IMAP Access**, select **Enable IMAP**
4. Click **Save Changes**

### 1b. Create App Password
1. Go to: https://myaccount.google.com/security
2. Click **2-Step Verification** (enable it if not already enabled)
3. Scroll down → Click **App passwords**
4. Under "Select app" choose **Mail**
5. Under "Select device" choose **Windows Computer**
6. Click **Generate**
7. **Copy the 16-character password** shown (e.g. `xxxx xxxx xxxx xxxx`)

> 💡 You already have an app password in your Acer script: `bbny ginj necl qdsv`
> You can try using that same one, OR generate a new one for this bot.

---

## STEP 2 — Create GitHub Repository

1. Go to **https://github.com** and log in as `armeebaroda@gmail.com`
2. Click the **+** button (top right) → **New repository**
3. Set:
   - Repository name: `gmail-whatsapp-bot`
   - Visibility: **Private** ✅ (keeps your credentials safe)
   - **Do NOT** initialize with README (we'll push our own files)
4. Click **Create repository**
5. **Copy the repository URL** — looks like:
   `https://github.com/armeebaroda/gmail-whatsapp-bot.git`

---

## STEP 3 — Add GitHub Secrets

> This is where your credentials are stored safely (not visible in code).

1. Go to your new repo on GitHub
2. Click **Settings** (top menu) → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each of these:

| Secret Name          | Value                                      |
|----------------------|--------------------------------------------|
| `GMAIL_ADDRESS`      | `jignesh.patel@armeeinfotech.com`           |
| `GMAIL_APP_PASSWORD` | Your 16-char app password (e.g. `bbny ginj necl qdsv`) |
| `WHATSAPP_PHONE`     | `+919327189050`                             |
| `CALLMEBOT_API_KEY`  | The API key CallMeBot sent you in Step 0   |

> ⚠️ Add all 4 secrets. The bot will fail silently if any are missing.

---

## STEP 4 — Upload Files to GitHub

Open **Command Prompt** in Windows (press Win+R → type `cmd` → Enter) and run:

```batch
cd d:\Office\Automatization\Whatsapp

git init
git add .
git commit -m "Initial commit: Gmail WhatsApp Bot"
git branch -M main
git remote add origin https://github.com/armeebaroda/gmail-whatsapp-bot.git
git push -u origin main
```

> If asked for username: `armeebaroda`
> If asked for password: use a **GitHub Personal Access Token** (not your GitHub password)
>
> To create a token: GitHub → Settings → Developer settings → Personal access tokens
> → Tokens (classic) → Generate new token → Check **repo** scope → Generate → Copy

---

## STEP 5 — Verify Deployment

### Manual Test (run immediately without waiting 1 hour)
1. Go to your GitHub repo
2. Click **Actions** tab (top menu)
3. Click **Gmail WhatsApp Hourly Summary** (left sidebar)
4. Click **Run workflow** button (right side)
5. Click the green **Run workflow** button in the popup
6. Wait ~30 seconds → Click the running job to see logs
7. Check your **WhatsApp** for the summary message!

---

## STEP 6 — Test Locally (Optional)

If you want to test on your PC before pushing to GitHub:

```batch
cd d:\Office\Automatization\Whatsapp
pip install requests

set GMAIL_ADDRESS=jignesh.patel@armeeinfotech.com
set GMAIL_APP_PASSWORD=bbny ginj necl qdsv
set WHATSAPP_PHONE=+919327189050
set CALLMEBOT_API_KEY=YOUR_KEY_FROM_CALLMEBOT

python main.py --test-gmail
python main.py --test-whatsapp
python main.py --once
```

---

## How It Runs Automatically

The bot runs **every hour at :30 minutes past** (e.g. 1:30, 2:30, 3:30...) using
GitHub Actions scheduled cron jobs. This is completely free.

GitHub Actions Free Tier: **2,000 minutes/month**
Each bot run takes ~1–2 minutes → 24 runs/day × 2 min = **48 min/day = ~1,440 min/month**
Easily within the free limit! ✅

---

## How to Reply to an Email

When you receive a summary and want to reply to email #2:

1. Open **Gmail on your phone**
2. Compose a new email **to yourself** (`jignesh.patel@armeeinfotech.com`)
3. Subject: **`BOT-REPLY-2`**
4. Body: **Your reply message**
5. Send it

The bot will pick it up on its **next hourly run** and send your reply to the original sender.
You'll get a WhatsApp confirmation when it's done.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "IMAP authentication failed" | Check App Password, make sure IMAP is enabled in Gmail |
| WhatsApp not received | Re-activate CallMeBot (API key expires if not used for 30 days) |
| "No module named requests" | Run: `pip install requests` |
| Bot not running hourly | Check GitHub Actions → see if workflow is enabled (not paused) |
| Replies not being sent | Make sure subject is exactly `BOT-REPLY-2` (with the dash) |
| armeeinfotech IMAP blocked | Ask your IT admin to enable IMAP for Google Workspace |

---

## File Structure Summary

```
d:\Office\Automatization\Whatsapp\     (this folder = GitHub repo root)
├── .github\
│   └── workflows\
│       └── hourly_summary.yml        ← GitHub Actions schedule
├── main.py                           ← Entry point (called by GitHub Actions)
├── config.py                         ← Configuration (reads env variables)
├── gmail_reader.py                   ← Gmail IMAP fetcher
├── email_summarizer.py               ← Rule-based email classifier
├── whatsapp_sender.py                ← CallMeBot API sender
├── reply_handler.py                  ← BOT-REPLY email processor
├── state_manager.py                  ← Saves/loads last-processed timestamp
├── state.json                        ← Auto-updated by bot each run
├── requirements.txt                  ← Python dependencies (just 'requests')
└── setup_guide.md                    ← This file
```

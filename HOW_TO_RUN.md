# 🚀 HOW TO RUN THE BOT — Complete Step-by-Step Guide

---

## ✅ CHECKLIST — Do These in Order

- [ ] STEP 0 — Activate CallMeBot (get your free WhatsApp API key)
- [ ] STEP 1 — Enable Gmail IMAP
- [ ] STEP 2 — Get Gmail App Password
- [ ] STEP 3 — Create GitHub Repository
- [ ] STEP 4 — Add Secrets to GitHub
- [ ] STEP 5 — Push Code to GitHub (one command)
- [ ] STEP 6 — Run Test (click one button in GitHub)
- [ ] STEP 7 — Check WhatsApp ✅

---

## STEP 0 — Fix WhatsApp / Get CallMeBot API Key

**On your phone:**
1. Open **WhatsApp**
2. Tap the **pencil icon** (new chat) → search `+34 644 52 40 45`
3. If you can't find it, open this link on your phone:
   👉 `https://wa.me/34644524045?text=I%20allow%20callmebot%20to%20send%20me%20messages`
4. Send the message: `I allow callmebot to send me messages`
5. Within 2 minutes they reply with your **API key** example: `1234567`
6. **Write down this API key** — you need it in Step 4

---

## STEP 1 — Enable Gmail IMAP

1. Open **Gmail** in browser (jignesh.patel@armeeinfotech.com)
2. Click the **⚙ gear icon** (top right)
3. Click **"See all settings"**
4. Click the **"Forwarding and POP/IMAP"** tab
5. Under **"IMAP Access"** → click **"Enable IMAP"**
6. Click **"Save Changes"** button at the bottom

---

## STEP 2 — Get Gmail App Password

> You might already have one: `bbny ginj necl qdsv` (from your Acer script)
> Skip to Step 3 if you want to try using that one first.

**To create a new App Password:**
1. Go to: `https://myaccount.google.com/security`
2. Click **"2-Step Verification"** (turn it on if not already on)
3. Scroll to the bottom → click **"App passwords"**
4. App: select **Mail**  |  Device: select **Windows Computer**
5. Click **Generate**
6. **Copy the 16-character password** shown (e.g. `abcd efgh ijkl mnop`)

---

## STEP 3 — Create GitHub Repository

1. Go to: `https://github.com/new` (log in as armeebaroda@gmail.com)
2. Fill in:
   - **Repository name:** `gmail-whatsapp-bot`
   - **Visibility:** 🔒 **Private** (important — keeps credentials safe)
   - ❌ Do NOT check "Add a README file"
3. Click **"Create repository"** (green button)
4. You'll see a page with setup instructions — **ignore those**

---

## STEP 4 — Add 4 Secrets to GitHub

1. In your new repository, click **"Settings"** (top menu bar)
2. In the left sidebar → click **"Secrets and variables"** → **"Actions"**
3. Click **"New repository secret"** and add these ONE BY ONE:

```
Name:   GMAIL_ADDRESS
Value:  jignesh.patel@armeeinfotech.com
```
```
Name:   GMAIL_APP_PASSWORD
Value:  bbny ginj necl qdsv
        (or your new app password from Step 2)
```
```
Name:   WHATSAPP_PHONE
Value:  +919327189050
```
```
Name:   CALLMEBOT_API_KEY
Value:  (the number CallMeBot sent you in Step 0)
```

> After adding all 4, you should see them listed under "Repository secrets"

---

## STEP 5 — Push Code to GitHub

**Open Command Prompt** (Press `Win + R` → type `cmd` → press Enter)

Copy and paste these commands ONE LINE AT A TIME:

```batch
cd d:\Office\Automatization\Whatsapp
```
```batch
git init
```
```batch
git add .
```
```batch
git commit -m "Initial commit: Gmail WhatsApp Bot"
```
```batch
git branch -M main
```
```batch
git remote add origin https://github.com/armeebaroda/gmail-whatsapp-bot.git
```
```batch
git push -u origin main
```

> ⚠️ When asked for **Username**: type `armeebaroda`
> ⚠️ When asked for **Password**: you need a GitHub Token (see below)

### 🔑 Creating a GitHub Token (needed for git push)
1. Go to: `https://github.com/settings/tokens/new`
2. Note: `gmail-bot-push`
3. Expiration: **No expiration**
4. Check the box: ✅ **repo** (full control)
5. Click **"Generate token"** → **Copy the token immediately**
6. Use this token as the **password** when git asks

---

## STEP 6 — Run the Bot Now (Manual Test)

1. Go to your GitHub repo: `https://github.com/armeebaroda/gmail-whatsapp-bot`
2. Click the **"Actions"** tab (top menu)
3. On the left sidebar, click **"Gmail WhatsApp Hourly Summary"**
4. Click the **"Run workflow"** button (right side, has dropdown arrow)
5. Click the green **"Run workflow"** button in the popup
6. Wait ~30 seconds
7. Click the running job (yellow dot → then click the job name)
8. Watch the live logs to see it working!

---

## STEP 7 — Check Your WhatsApp 📱

Within 1 minute of running Step 6, you should receive a WhatsApp message like:

```
📧 GMAIL HOURLY SUMMARY
🕐 1:00 PM – 2:00 PM | 3 New Emails

━━━━━━━━━━━━━━━━━━━━━━
🔴 URGENT – Reply Needed (1)
━━━━━━━━━━━━━━━━━━━━━━
1. Jinal Ranapariya
   📌 OEM Ticket Escalation
   ↳ Customer needs immediate response...

━━━━━━━━━━━━━━━━━━━━━━
🟡 ACTION NEEDED (2)
...
```

---

## ⏰ Automatic Schedule

After this one-time setup, the bot runs **automatically every hour** — even when
your PC is off. No further action needed!

**Times (IST):** 6:00, 7:00, 8:00, 9:00... every hour all day and night.

---

## 💬 How to Reply to an Email from WhatsApp Summary

When summary says email #2 needs reply:
1. Open **Gmail on your phone**
2. Compose new email **to yourself**
3. Subject: **`BOT-REPLY-2`**
4. Body: **Your reply message**
5. Send → Bot will send the reply on next hour's run ✅

---

## ❓ Common Problems

| Problem | Fix |
|---------|-----|
| "Authentication failed" in logs | Check App Password is correct, IMAP is enabled |
| No WhatsApp received | Redo Step 0 — re-activate CallMeBot |
| git push asks for password | Use the GitHub Token (not your password) |
| Workflow not visible in Actions tab | Push the code first (Step 5), then check |
| "CALLMEBOT_API_KEY not set" | Add the secret in Step 4 |

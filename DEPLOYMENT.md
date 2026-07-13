# Deploying Churchgate HRIS to Railway

This is a Streamlit app. Railway builds it with Nixpacks (auto-detected from
`requirements.txt`) and runs `start.sh`, which generates the Streamlit config +
secrets from service variables and launches the app on Railway's `$PORT`.

## 1. Create the Railway service

1. Push this repo to GitHub (see the security note below first).
2. Railway → **New Project → Deploy from GitHub repo** → pick this repo/branch.
3. Railway auto-detects Python. `railway.json` sets the start command
   (`bash start.sh`) and a health check on `/_stcore/health`.

## 2. Set service variables (Railway → service → Variables)

Required:

| Variable        | Value                                  |
| --------------- | -------------------------------------- |
| `SUPABASE_URL`  | your Supabase project URL              |
| `SUPABASE_KEY`  | Supabase anon/publishable key          |
| `SMTP_EMAIL`    | Gmail address used to send mail        |
| `SMTP_PASSWORD` | Gmail **app password** (not login pwd) |

Optional (only if used): `OPENAI_API_KEY`, `SLACK_WEBHOOK_URL`,
`TEAMS_WEBHOOK_URL`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`,
`TWILIO_WHATSAPP_NUMBER`, `ASANA_PERSONAL_TOKEN`, `ASANA_WORKSPACE_ID`,
`GOOGLE_CALENDAR_API_KEY`.

Do **not** set `PORT` — Railway injects it automatically.

## 3. Custom subdomain via Cloudflare

1. Railway → service → **Settings → Networking → Custom Domain** →
   enter e.g. `hris.yourdomain.com`. Railway shows a **CNAME target**
   (like `xxxx.up.railway.app`).
2. Cloudflare → your domain → **DNS → Add record**:
   - Type: `CNAME`
   - Name: `hris` (the subdomain)
   - Target: the Railway CNAME target
   - Proxy status: **DNS only (grey cloud)** for the first verification.
     Once Railway shows the domain as verified and TLS is issued, you may
     switch to **Proxied (orange cloud)**.
3. SSL/TLS mode in Cloudflare: set to **Full** (or **Full (strict)**) so
   Cloudflare talks to Railway over HTTPS. "Flexible" will cause redirect loops.
4. Streamlit uses WebSockets — Cloudflare proxies these automatically, no extra
   config needed. `start.sh` already disables CORS/XSRF for proxy compatibility.

## Security note — rotate the SMTP password

`.env` (containing `SMTP_PASSWORD`) was previously committed to git history.
It is now removed from tracking and gitignored, but **the old value still exists
in past commits**. Rotate that Gmail app password before/after making the repo
public, and keep secrets only in Railway variables from now on.

## Local development

```bash
cp .env.example .env            # fill in values
# put the same values in .streamlit/secrets.toml (app reads st.secrets)
bash run_app.sh
```

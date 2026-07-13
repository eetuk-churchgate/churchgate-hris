#!/usr/bin/env bash
# Railway / container entrypoint for the Churchgate HRIS Streamlit app.
# Streamlit reads configuration from st.secrets, which loads .streamlit/secrets.toml.
# Streamlit does NOT read OS environment variables automatically, so we materialize
# a secrets.toml from the Railway service variables at boot (nothing secret is committed).
set -euo pipefail

mkdir -p .streamlit

# --- Streamlit server config (running behind Railway + Cloudflare proxy) ---
cat > .streamlit/config.toml <<EOF
[server]
headless = true
address = "0.0.0.0"
port = ${PORT:-8501}
enableCORS = false
enableXsrfProtection = false
[browser]
gatherUsageStats = false
EOF

# --- Materialize secrets.toml from environment variables ---
# Only variables that are actually set are written.
emit() {
  local key="$1"; local val="${2:-}"
  if [ -n "$val" ]; then
    # Escape any embedded double-quotes for TOML safety.
    val="${val//\"/\\\"}"
    echo "${key} = \"${val}\""
  fi
}

{
  emit SUPABASE_URL           "${SUPABASE_URL:-}"
  emit SUPABASE_KEY           "${SUPABASE_KEY:-}"
  emit SMTP_SERVER            "${SMTP_SERVER:-}"
  emit SMTP_PORT              "${SMTP_PORT:-}"
  emit SMTP_USERNAME          "${SMTP_USERNAME:-}"
  emit SMTP_SENDER_EMAIL      "${SMTP_SENDER_EMAIL:-}"
  emit SMTP_SENDER_NAME       "${SMTP_SENDER_NAME:-}"
  emit SMTP_EMAIL             "${SMTP_EMAIL:-}"
  emit SMTP_PASSWORD          "${SMTP_PASSWORD:-}"
  emit OPENAI_API_KEY         "${OPENAI_API_KEY:-}"
  emit SLACK_WEBHOOK_URL      "${SLACK_WEBHOOK_URL:-}"
  emit TEAMS_WEBHOOK_URL      "${TEAMS_WEBHOOK_URL:-}"
  emit TWILIO_ACCOUNT_SID     "${TWILIO_ACCOUNT_SID:-}"
  emit TWILIO_AUTH_TOKEN      "${TWILIO_AUTH_TOKEN:-}"
  emit TWILIO_WHATSAPP_NUMBER "${TWILIO_WHATSAPP_NUMBER:-}"
  emit ASANA_PERSONAL_TOKEN   "${ASANA_PERSONAL_TOKEN:-}"
  emit ASANA_WORKSPACE_ID     "${ASANA_WORKSPACE_ID:-}"
  emit GOOGLE_CALENDAR_API_KEY "${GOOGLE_CALENDAR_API_KEY:-}"
} > .streamlit/secrets.toml

# Inject Churchgate branding + Open Graph tags into Streamlit's served HTML so
# shared links show a proper preview card (best-effort; never blocks startup).
python scripts/patch_streamlit_meta.py || true

exec streamlit run app.py --server.port "${PORT:-8501}" --server.address 0.0.0.0

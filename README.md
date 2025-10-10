# Appointment Bot (Meta + Telegram)

Production-grade FastAPI service that normalizes appointment booking conversations across Meta (Messenger + Instagram) and Telegram. Local-first setup with SQLite persistence, OpenAI-powered NLU, and optional Google Sheets mirroring.

## Features
- Meta + Telegram webhook receivers with signature/secret validation
- GPT-4o-mini NLU for intent detection and slot filling
- Rate-limited conversational orchestration with SQLite persistence
- Optional Google Sheets mirroring via service accounts
- CLI helpers for webhook/bootstrap and GitHub shipping
- Full developer toolchain (lint, typecheck, tests) and GitHub Actions CI

## Quickstart
1. Copy env template and fill values:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies:
   ```bash
   make install
   ```
3. Run the service locally:
   ```bash
   make run
   ```
4. Expose your service (e.g. ngrok or cloudflared) to make `${BASE_URL}` public.
5. Configure Telegram webhook with your tunnel URL:
   ```bash
   python scripts/bootstrap_telegram.py
   ```
6. Subscribe your Meta page/app to receive messages:
   ```bash
   bash scripts/subscribe_meta.sh
   ```
7. Configure the Meta webhook URL to `${PUBLIC_URL}/webhook/meta` using the `META_VERIFY_TOKEN` you set in `.env`.

## Webhooks
- `GET  /webhook/meta` – Verification handshake with `hub.challenge`
- `POST /webhook/meta` – Messenger + Instagram inbound
- `POST /webhook/telegram` – Telegram inbound with secret token guard
- `GET  /health` – Service health check

## Example Requests
Meta verification:
```bash
curl "${PUBLIC_URL}/webhook/meta?hub.mode=subscribe&hub.verify_token=${META_VERIFY_TOKEN}&hub.challenge=123"
```

Send a test Telegram message:
```bash
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "<CHAT_ID>", "text": "Hi! I'd like a haircut tomorrow at 3pm"}'
```

## Troubleshooting
- **Meta Graph API 400s**: Double-check the Page access token scope and ensure the page is subscribed to the app. Inspect `response.text` from logs for more detail.
- **Instagram vs Messenger**: Instagram requires `IG_BUSINESS_ID` for send API calls; Messenger uses `/me/messages`.
- **Signature mismatch**: Confirm `META_APP_SECRET` matches the app secret in Meta Developer settings and that your tunnel forwards raw request bodies.
- **Telegram webhook**: Ensure the secret token matches `TELEGRAM_SECRET_TOKEN`; Telegram must return HTTP 200 to avoid retries.

## Security Notes
- Secrets should be stored via environment variables or a secrets manager; `.env` is for local development only.
- Logs exclude message bodies and secrets; avoid adding sensitive data to structured logging.
- Rotate API keys and tokens regularly, especially when sharing tunnel URLs.

## Developer Tooling
- `make lint` – Ruff linting
- `make format` – Black formatting
- `make typecheck` – mypy static analysis
- `make test` – Pytest with coverage report
- `make dev` – Run FastAPI locally with uvicorn

## Google Sheets Sync
Provide either `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64` (preferred) or `GOOGLE_SERVICE_ACCOUNT_FILE`. When configured, confirmed bookings append to the sheet with headers `timestamp,name,service,date,time,phone`.

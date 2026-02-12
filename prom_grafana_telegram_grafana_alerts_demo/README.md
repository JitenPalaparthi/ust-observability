# Grafana → Telegram Alerts (using Grafana Alerting) + Prometheus + Python Metrics App

This demo sends **Telegram notifications from Grafana Alerting** (NOT from Prometheus Alertmanager).

Stack:
- Python (Flask) app exports Prometheus metrics
- Prometheus scrapes the app (as a data source for Grafana)
- Grafana evaluates alert rules and sends Telegram notifications via **Contact Points**

## Prereqs
- Docker + Docker Compose
- Telegram bot token + chat_id

## 1) Create Telegram Bot + Get chat_id
1. In Telegram, message **@BotFather**:
   - `/newbot` → create a bot → copy the **BOT_TOKEN**
2. Get your **chat_id**:
   - Start a chat with your bot and send any message (e.g., "hi")
   - Open:
     `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
   - Find: `"chat":{"id":123456789,...}` → that's your **CHAT_ID**
   - (For a group: add the bot to the group, send a message, then use getUpdates; chat_id will be negative like -100xxxx)

## 2) Run the stack
```bash
docker compose up --build
```

Endpoints:
- Python app: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin / admin)

## 3) Confirm metrics
Open:
- http://localhost:8000/metrics

Trigger an "error" increment:
```bash
curl -X POST http://localhost:8000/trigger-error
```

## 4) Configure Telegram in Grafana (UI)
Grafana has a built-in **Telegram contact point**.

1. Open Grafana: http://localhost:3000 (admin/admin)
2. Go to: **Alerts & IRM → Alerting → Contact points**
3. Click **+ Add contact point**
4. Integration: **Telegram**
5. Fill:
   - **BOT API Token** = your bot token
   - **Chat ID** = your chat id
6. Click **Test** (you should receive a Telegram message)
7. Save

(Reference: Grafana docs “Configure Telegram for Alerting”.)

## 5) Create an alert rule in Grafana (UI)
1. Go to: **Alerts & IRM → Alerting → Alert rules**
2. **New alert rule**
3. Data source: **Prometheus**
4. Query (A):
   - `rate(demo_errors_total[1m])`
5. Condition:
   - WHEN last() OF A IS ABOVE 0
6. Set:
   - Evaluation interval: 10s (demo)
   - For: 30s
7. Add labels (optional):
   - severity="warning"
8. Save

## 6) Route alerts to Telegram (Notification policy)
1. Go to: **Alerts & IRM → Alerting → Notification policies**
2. Ensure the **Default policy** (or a new policy matching labels) routes to your Telegram contact point.

## 7) Trigger the alert
Send a few increments:
```bash
for i in $(seq 1 3); do curl -s -X POST http://localhost:8000/trigger-error >/dev/null; sleep 1; done
```

Within ~1–2 minutes, Grafana should fire and Telegram should receive the alert.

## Troubleshooting
- Check alert evaluation: **Alert rules → “View state”**
- Ensure the notification policy matches your labels (or use Default policy).
- Grafana logs:
  `docker compose logs -f grafana`

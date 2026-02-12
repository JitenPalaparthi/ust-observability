# Prometheus + Grafana + Python App + Telegram Alerts (Demo)

This repo demonstrates:
- A **Python** web app exporting Prometheus metrics
- **Prometheus** scraping the app + evaluating alert rules
- **Alertmanager** sending **Telegram notifications**
- **Grafana** to visualize metrics

## Prereqs
- Docker + Docker Compose
- A Telegram bot token + a chat_id

## 1) Create Telegram Bot + Get chat_id
1. In Telegram, message **@BotFather**:
   - `/newbot` → create a bot → copy the **BOT_TOKEN**
2. Get your **chat_id**:
   - Start a chat with your bot and send any message (e.g., "hi")
   - Open in browser:
     `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
   - Find: `"chat":{"id":123456789,...}` → that's your **CHAT_ID**
   - (For a group: add the bot to the group, send a message, then use getUpdates; chat_id will be negative like -100xxxx)

## 2) Configure secrets
Copy `.env.example` → `.env` and fill values:

```bash
cp .env.example .env
# edit .env
```

## 3) Run the stack
```bash
docker compose up --build
```

- Python app: http://localhost:8000
- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093
- Grafana: http://localhost:3000 (admin / admin)

## 4) Trigger an alert
The demo includes a counter `demo_errors_total`.

Trigger errors:
```bash
curl -X POST http://localhost:8000/trigger-error
```

Watch metrics:
- http://localhost:8000/metrics

Within ~1–2 minutes, Prometheus should fire **DemoHighErrorRate** and Alertmanager will send a Telegram message.

## 5) Grafana
A Prometheus datasource is auto-provisioned.
Create a quick panel with:
- `rate(demo_requests_total[1m])`
- `rate(demo_errors_total[1m])`

## Notes / Troubleshooting
- If Telegram alerts don't arrive:
  - Verify BOT_TOKEN and CHAT_ID
  - Ensure you have sent at least one message to the bot (so getUpdates shows your chat)
  - Check Alertmanager logs: `docker compose logs -f alertmanager`
- This is a minimal demo; for production you should:
  - Use TLS, auth, and proper routing
  - Rate-limit noisy alerts
  - Use grouping/inhibition, dedupe keys, and runbook URLs



@botfather /newbot
bot name: ust_observability_demo_bot
bot user: ust_observability_demo_user_bot



Send a message to the above user in telegram->/start 

group: group_ust_observability_demo_user

bot token: 8518446092:AAH-xiaLjMBoZwN8btro7076JT9-d8_75KM

- To get ID, hit the following URL: https://api.telegram.org/bot8518446092:AAH-xiaLjMBoZwN8btro7076JT9-d8_75KM/getUpdates

{"ok":true,"result":[{"update_id":363455590,
"message":{"message_id":3,"from":{"id":498634016,"is_bot":false,"first_name":"JP","username":"Jitenp","language_code":"en"},"chat":{"id":498634016,"first_name":"JP","username":"Jitenp","type":"private"},"date":1770876423,"text":"/start","entities":[{"offset":0,"length":6,"type":"bot_command"}]}},{"update_id":363455591,
"message":{"message_id":4,"from":{"id":498634016,"is_bot":false,"first_name":"JP","username":"Jitenp","language_code":"en"},"chat":{"id":-5120718211,"title":"group_ust_observability_demo_user","type":"group","all_members_are_administrators":true,"accepted_gift_types":{"unlimited_gifts":false,"limited_gifts":false,"unique_gifts":false,"premium_subscription":false,"gifts_from_channels":false}},"date":1770876455,"left_chat_participant":{"id":498634016,"is_bot":false,"first_name":"JP","username":"Jitenp","language_code":"en"},"left_chat_member":{"id":498634016,"is_bot":false,"first_name":"JP","username":"Jitenp","language_code":"en"}}},{"update_id":363455592,
"my_chat_member":{"chat":{"id":-5120718211,"title":"group_ust_observability_demo_user","type":"group","all_members_are_administrators":true,"accepted_gift_types":{"unlimited_gifts":false,"limited_gifts":false,"unique_gifts":false,"premium_subscription":false,"gifts_from_channels":false}},"from":{"id":498634016,"is_bot":false,"first_name":"JP","username":"Jitenp","language_code":"en"},"date":1770876455,"old_chat_member":{"user":{"id":8518446092,"is_bot":true,"first_name":"ust_observability_demo_bot","username":"ust_observability_demo_user_bot"},"status":"member"},"new_chat_member":{"user":{"id":8518446092,"is_bot":true,"first_name":"ust_observability_demo_bot","username":"ust_observability_demo_user_bot"},"status":"left"}}},{"update_id":363455593,
"my_chat_member":{"chat":{"id":-5283241807,"title":"group_ust_observability_demo_user","type":"group","all_members_are_administrators":true,"accepted_gift_types":{"unlimited_gifts":false,"limited_gifts":false,"unique_gifts":false,"premium_subscription":false,"gifts_from_channels":false}},"from":{"id":498634016,"is_bot":false,"first_name":"JP","username":"Jitenp","language_code":"en"},"date":1770876501,"old_chat_member":{"user":{"id":8518446092,"is_bot":true,"first_name":"ust_observability_demo_bot","username":"ust_observability_demo_user_bot"},"status":"left"},"new_chat_member":{"user":{"id":8518446092,"is_bot":true,"first_name":"ust_observability_demo_bot","username":"ust_observability_demo_user_bot"},"status":"member"}}},{"update_id":363455594,
"message":{"message_id":5,"from":{"id":498634016,"is_bot":false,"first_name":"JP","username":"Jitenp","language_code":"en"},"chat":{"id":-5283241807,"title":"group_ust_observability_demo_user","type":"group","all_members_are_administrators":true,"accepted_gift_types":{"unlimited_gifts":false,"limited_gifts":false,"unique_gifts":false,"premium_subscription":false,"gifts_from_channels":false}},"date":1770876501,"group_chat_created":true}}]}

chat id: -5120718211
# Grafana + Prometheus + Python (Flask) demo with multiple dashboards

## What you get
- Python app exposing Prometheus metrics on `/metrics` and demo endpoint `/work`
- Prometheus scraping the app + Prometheus itself
- Grafana auto-provisioned:
  - Prometheus datasource (default)
  - 3 dashboards (imported automatically on startup)

## Quick start
```bash
docker compose up -d
```

Generate some traffic:
```bash
# hit this multiple times
curl -s http://localhost:8000/work
```

Open:
- Python app: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000  (admin / admin)

Dashboards appear under: **Dashboards -> Browse -> Provisioned**

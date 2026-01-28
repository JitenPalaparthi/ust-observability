# Python Prometheus Metrics Demo (Docker + Prometheus)

This is a minimal, production-style demo that exposes Prometheus metrics from a Python web service and scrapes them using Prometheus via Docker Compose.

## What you get
- `app` (Flask) exposing:
  - `GET /` – basic endpoint that *also* increments a counter and records latency
  - `GET /work?ms=120` – simulates work for `ms` milliseconds and records metrics
  - `GET /metrics` – Prometheus metrics endpoint (Prometheus scrape target)
- `prometheus` – scrapes `app:8000/metrics` every 5 seconds

## Run
```bash
docker compose up --build
```

### URLs
- App: http://localhost:8000/
- Metrics: http://localhost:8000/metrics
- Prometheus UI: http://localhost:9090/

## Try generating some traffic
In another terminal:
```bash
# hit / a few times
curl -s http://localhost:8000/ >/dev/null
curl -s http://localhost:8000/ >/dev/null

# simulate varying work
curl -s "http://localhost:8000/work?ms=50" >/dev/null
curl -s "http://localhost:8000/work?ms=200" >/dev/null
curl -s "http://localhost:8000/work?ms=800" >/dev/null
```

## Prometheus queries (examples)
Open Prometheus (9090) → Graph tab:

- Total requests:
  - `demo_requests_total`

- Requests per second (rate over 1 minute):
  - `rate(demo_requests_total[1m])`

- Latency (p95 over 5 minutes) for `/` and `/work`:
  - `histogram_quantile(0.95, sum(rate(demo_request_duration_seconds_bucket[5m])) by (le, route))`

- In-progress requests (gauge):
  - `demo_inprogress_requests`

- App info (gauge with labels):
  - `demo_app_info`

## Metrics explained (what they mean)
This demo uses Prometheus *types* you’ll use in real services:

### Counter: `demo_requests_total{route,method,status}`
Monotonic increasing count of requests.
- Use in dashboards and alerting with `rate()` or `increase()`.

### Histogram: `demo_request_duration_seconds_bucket{le,route}`
Request duration distribution.
- Prometheus also creates:
  - `_sum` and `_count`
- Use `histogram_quantile()` for p50/p95/p99.

### Gauge: `demo_inprogress_requests`
Number of requests currently being processed.

### Gauge (info-style): `demo_app_info{service,version,env}`
Always set to `1` and used as an “info” label carrier.

## Notes
- This demo runs Flask with `gunicorn` for a realistic deployment model.
- If you want multi-process correctness for counters/histograms under gunicorn workers, you’d enable Prometheus multiprocess mode. For simplicity, this demo uses a single worker.

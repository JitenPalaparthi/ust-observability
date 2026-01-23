# OpenTelemetry Metrics Demo (Works even if your host Python is 3.14)

This project avoids host-side Python dependency issues by running the **Python app in Docker** (Python 3.12),
while still giving you the full pipeline:

**Python (OTLP) → OpenTelemetry Collector → Prometheus**, plus **debug output**.

## Architecture

- `app` (Python 3.12 container) emits OpenTelemetry metrics via **OTLP HTTP**
- `collector` receives OTLP, exports:
  - `prometheus` exporter at `:9464/metrics`
  - `debug` exporter (prints metrics in collector logs)
- `prometheus` scrapes the collector and provides UI at `:9090`

## Files

- `docker-compose.yml` – starts app + collector + prometheus
- `otel-collector-config.yaml` – OTLP receiver + Prometheus + debug exporter
- `prometheus.yml` – scrape config
- `app/` – Python application + Dockerfile + requirements

## Prerequisites

- Docker Desktop (or Docker Engine)
- Docker Compose

No Python is required on the host machine.

## Run

From the project directory:

```bash
docker compose up -d --build
```

### Watch logs (debug)

Collector logs (shows metrics via debug exporter):

```bash
docker compose logs -f collector
```

App logs:

```bash
docker compose logs -f app
```

## Verify

### Prometheus UI
Open:

- http://localhost:9090

Go to **Status → Targets** and ensure `otel-collector` is **UP**.

### Example PromQL queries

```promql
demo_demo_requests_total
demo_demo_request_latency_ms_bucket
demo_demo_queue_depth
```

### Check collector metrics endpoint directly (optional)

```bash
curl http://localhost:9464/metrics | head
```

## Stop

```bash
docker compose down
```

## Notes

- This is a demo baseline. You can extend it to add traces/logs, Grafana, or Kubernetes manifests.

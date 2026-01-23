# OpenTelemetry Python Logs → OTel Collector → Loki → Grafana (WORKING DEMO)

This demo works even if your host Python is 3.14 because the Python app runs in Docker (Python 3.12).

## Run

```bash
docker compose up -d --build
```

## Debug

Collector (shows what it receives + exports, via `debug` exporter):

```bash
docker compose logs -f otel-collector
```

App logs:

```bash
docker compose logs -f app
```

## Grafana

Open: http://localhost:3000  
Login: admin / admin

Explore → Loki.

### Queries that should work

All logs:

```logql
{}
```

By service (note: Loki converts `service.name` to `service_name` label):

```logql
{service_name="python-otel-logs-demo"}
```

By environment (from `service.environment` → `service_environment`):

```logql
{service_environment="dev"}
```

By custom label (from log attribute `custom_key`, promoted via `loki.attribute.labels`):

```logql
{custom_key="demo"}
```

## Why this works

The Loki exporter supports **hint attributes** to decide what becomes a Loki label:

- `loki.resource.labels`: which resource attributes to promote to labels
- `loki.attribute.labels`: which log attributes to promote to labels

This avoids deprecated exporter-side label mapping and prevents config decode errors.

## Stop

```bash
docker compose down
```

Python app --> creates and expoert logs --> export to otel (otlp protocol) --> otel processes --> export to loki and debug 
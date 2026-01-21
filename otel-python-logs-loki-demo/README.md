# OpenTelemetry Python Logs -> OTel Collector -> Loki Demo

This demo shows how to send logs from a Python application using OpenTelemetry
to an OpenTelemetry Collector, and then export them to Loki. Grafana is also
included to visualize logs from Loki.

## Components

- **app**: Python application using `logging` + OpenTelemetry logging bridge.
- **otel-collector**: Receives OTLP logs and exports to Loki.
- **loki**: Log storage and query backend.
- **grafana**: UI to query logs from Loki.

## How to Run

1. Make sure you have Docker and Docker Compose installed.

2. From the project root (where `docker-compose.yml` is located), run:

```bash
docker compose up --build
```

3. The Python app will start emitting logs every 2 seconds. Logs are sent via OTLP
   to the OTel Collector, which forwards them to Loki.

## Access Grafana

- URL: http://localhost:3000
- Default user: `admin`
- Default password: `admin` (as set in docker-compose)

### Configure Loki in Grafana

1. Log in to Grafana.
2. Go to **Configuration → Data sources → Add data source**.
3. Select **Loki**.
4. Set URL to: `http://loki:3100`
5. Click **Save & test**.

## Query Logs

In Grafana **Explore** view:

1. Select the Loki data source.
2. Use a query like:

```logql
{service_name="python-otel-logs-demo"}
```

You should see log lines emitted by the Python app, with labels derived from
OpenTelemetry resource attributes.

## Stopping the Demo

Press `Ctrl+C` in the terminal running:

```bash
docker compose up --build
```

Then optionally run:

```bash
docker compose down
```

to stop and remove containers.

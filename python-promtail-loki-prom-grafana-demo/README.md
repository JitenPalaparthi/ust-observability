
# Python Observability Demo
**Metrics + Logs + Traces using Prometheus, Loki, Grafana & Jaeger**

This project demonstrates **end-to-end observability** for a Python application using the Grafana stack.

---

## Architecture

```
Python App
 ├── Metrics  --> Prometheus --> Grafana
 ├── Logs     --> File --> Promtail --> Loki --> Grafana
 └── Traces   --> Jaeger --> Grafana
```

---

## Prerequisites

- Docker 20+
- Docker Compose v2+

Verify installation:

```bash
docker --version
docker compose version
```

---

## Project Structure

```
otel-demo/
├── docker-compose.yml
├── README.md
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── prometheus/
│   └── prometheus.yml
├── loki/
│   └── loki-config.yml
├── promtail/
│   └── promtail-config.yml
├── grafana/
│   └── provisioning/
│       └── datasources/
│           └── datasources.yml
└── logs/
    └── app.log   (created at runtime)
```

---

## Step 1: Start the stack

From the project root directory:

```bash
docker compose up --build
```

Wait until all containers are in **running** state.

---

## Step 2: Generate traffic

In another terminal:

```bash
curl http://localhost:8000/
curl http://localhost:8000/
curl http://localhost:8000/
```

This will generate:
- Metrics
- Logs
- Traces

---

## Metrics (Prometheus)

### Prometheus UI

```
http://localhost:9090
```

Query:

```
app_requests_total
```

---

## Metrics in Grafana

Grafana UI:

```
http://localhost:3000
```

Login:
```
admin / admin
```

Steps:
- Go to **Explore**
- Select **Prometheus**
- Run:

```
app_requests_total
```

---

## Logs (Loki)

In Grafana:

- Go to **Explore**
- Select **Loki**
- Run:

```
{job="py-app"}
```

You should see application logs.

---

## Traces (Jaeger)

### Jaeger UI

```
http://localhost:16686
```

Steps:
1. Select **Service** → `py-app`
2. Click **Find Traces**
3. Open a trace to see spans

---

## Traces in Grafana

- Grafana → **Explore**
- Select **Jaeger**
- Service: `py-app`

---

## Service URLs

| Service | URL |
|------|-----|
| Python App | http://localhost:8000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Jaeger | http://localhost:16686 |
| Loki | http://localhost:3100 |

---

## Stop the stack

```bash
docker compose down
```

---

## Notes

- This setup is intentionally **simple**
- No authentication
- Single-node services
- Ideal for learning and demos

---

## Next Improvements

- OpenTelemetry Collector
- Zipkin support
- Trace-ID log correlation
- Pre-built Grafana dashboards
- Kubernetes deployment

---

Happy Observing 🚀

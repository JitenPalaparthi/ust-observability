# OpenTelemetry Go + Docker + Jaeger + Context Propagation Demo

This demo shows two Go HTTP services (`service-a` and `service-b`) instrumented
with OpenTelemetry, exporting traces via OTLP to an OpenTelemetry Collector,
which forwards them to Jaeger.

It demonstrates **context propagation**:
- Client: Service A receives a request on `/hello` and calls Service B `/work`
  using an `otelhttp`-instrumented HTTP client with propagated context.
- Server: Service B's `/work` handler is wrapped with `otelhttp.NewHandler`,
  so it automatically extracts the incoming trace context and continues
  the same trace.

## Architecture

- `service-a` (port 8080)
  - Endpoint: `/hello`
  - Simulates work, starts spans, calls `service-b` using otelhttp client.

- `service-b` (port 8081)
  - Endpoint: `/work`
  - Receives propagated context, continues the trace, and adds attributes.

- `otel-collector`
  - Receives traces via OTLP/HTTP on port 4318.
  - Exports to Jaeger.

- `jaeger`
  - Jaeger all-in-one with UI on `http://localhost:16686`.

## Prerequisites

- Docker
- Docker Compose

## How to Run

From the project root (where `docker-compose.yml` is located):

```bash
docker compose up --build
```

Wait until all services are up (`service-a`, `service-b`, `otel-collector`, `jaeger`).

## Generate Traffic

In another terminal, run:

```bash
curl http://localhost:8080/hello
```

Or generate continuous traffic:

```bash
while true; do curl -s http://localhost:8080/hello > /dev/null; sleep 1; done
```

Each call to `/hello` on Service A will internally call Service B `/work` and
propagate the trace context.

## View Traces in Jaeger

1. Open Jaeger UI in your browser:

   - URL: http://localhost:16686

2. In the **Search** tab:
   - Service: select `service-a` or `service-b`
   - Click **Find Traces**

3. You should see traces where:
   - The root span is in `service-a` (e.g., `hello-handler`).
   - Child spans include:
     - `service-a-work`
     - `GET /work` from `service-a` client
     - `work-handler` in `service-b`

This demonstrates **end-to-end distributed tracing and context propagation**
between two services using OpenTelemetry.

## Stopping the Demo

Press `Ctrl+C` in the terminal running:

```bash
docker compose up --build
```

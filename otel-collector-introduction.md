# OpenTelemetry Collector (otelcol) — Introduction and Core Concepts

## 1. What is the OpenTelemetry Collector?

The **OpenTelemetry Collector** (often abbreviated as **otelcol**) is a vendor-neutral, production-grade **telemetry pipeline** that can **receive**, **process**, and **export** telemetry signals:

- **Traces**
- **Metrics**
- **Logs** (support depends on the build/components you use)

It is designed to decouple:
- **Instrumentation** (what your apps produce)
from
- **Backends** (where telemetry is stored/queried/visualized)

This enables a consistent, centralized approach to telemetry across environments and vendors.

### Why the Collector is used
- **Standardization**: normalize telemetry into OpenTelemetry data models.
- **Routing**: send the same signal to multiple destinations (e.g., Prometheus + OTLP + vendor).
- **Enrichment**: add attributes (environment, cluster, region, team ownership).
- **Governance**: filter sensitive data, enforce naming conventions, drop noisy signals.
- **Cost control**: sampling traces, filtering metrics/logs, batching.
- **Performance**: offload serialization/export overhead from applications.
- **Interoperability**: bridge between protocols/formats (Prometheus, OTLP, Jaeger, Zipkin, etc.).

---

## 2. Collector Builds: Core vs Contrib

You will commonly see two binaries/images:

- **otelcol (core)**: smaller set of components.
- **otelcol-contrib (contrib)**: superset with many receivers/exporters/processors (e.g., `hostmetrics`, `kubeletstats`, many vendor exporters).

If you need host and Kubernetes-level receivers, **contrib** is typically used.

---

## 3. How the Collector is structured (mental model)

Think of the Collector as a **dataflow engine**:

**Receivers** → **Processors** → **Exporters**  
assembled into **Pipelines**  
optionally supported by **Extensions**

Each pipeline is signal-specific (metrics/traces/logs).

---

## 4. Signals: Metrics vs Traces vs Logs (high-level)

### Metrics
- Numeric measurements over time (counters, gauges, histograms).
- Example: CPU utilization, request rate, latency histogram.

### Traces
- Distributed transaction context with spans.
- Example: a request passing through API gateway → service A → service B → database.

### Logs
- Timestamped records (events).
- Example: application logs, audit logs, structured logs.

---

## 5. Receivers (ingestion)

A **receiver** is an input component. It “receives” telemetry from:
- instrumented applications,
- agents,
- or by scraping/polling systems.

### Common receiver categories

#### A) Push-based receivers
Telemetry is **sent to the Collector**.

Examples:
- `otlp` (gRPC/HTTP): the standard OpenTelemetry protocol receiver.
- `jaeger`: receives Jaeger traces.
- `zipkin`: receives Zipkin traces.

#### B) Pull-based receivers
Collector **scrapes/polls** telemetry.

Examples:
- `prometheus`: scrapes metrics from targets.
- `hostmetrics`: reads system/host stats (CPU, memory, disk, network).
- `kubeletstats`: pulls metrics from kubelet/cAdvisor endpoints.

### Receiver configuration structure
A receiver has an ID and parameters:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:
  hostmetrics:
    collection_interval: 10s
    scrapers:
      cpu: {}
      memory: {}
```

Notes:
- Receivers are **declared once** and can be used in multiple pipelines.
- Each pipeline lists the receivers to use.

---

## 6. Processors (transform, enrich, control)

A **processor** modifies, filters, aggregates, batches, samples, or enriches telemetry *between receiving and exporting*.

### Why processors matter
Processors are where you implement:
- **data governance**
- **cardinality controls**
- **tenant routing**
- **sampling policies**
- **standard resource attributes**
- **privacy controls** (dropping or hashing attributes)

### Common processors and what they do

#### `batch`
Groups telemetry into batches for efficient export (reduces overhead, improves throughput).

Typical use:
```yaml
processors:
  batch: {}
```

#### `resource`
Adds or modifies **resource attributes** (attributes describing the producing entity: host, service, environment).

Example:
```yaml
processors:
  resource:
    attributes:
      - key: deployment.environment
        value: prod
        action: upsert
```

#### `attributes`
Adds/modifies span/log attributes (signal-level).

#### `filter`
Drops telemetry that matches conditions (noise reduction, cost control).

#### `memory_limiter`
Protects collector from OOM by backpressure and dropping.

#### `tail_sampling` (traces)
Samples traces based on full trace content (high quality sampling) but requires buffering.

#### `probabilistic_sampler` (traces)
Random sampling by percentage.

#### `metricstransform` / `transform`
Rename metrics, change units, drop attributes, etc. (useful for standardization).

### Processor ordering is important
Example: you often want:
- `memory_limiter` early,
- `resource` before exporters,
- `batch` near the end.

---

## 7. Exporters (delivery to backends)

An **exporter** sends telemetry to destinations:
- observability backends (Tempo/Jaeger/Zipkin),
- metric stores (Prometheus remote_write, Mimir, VictoriaMetrics),
- log systems (Loki, Elasticsearch),
- SaaS vendors,
- or for debugging.

### Common exporter types

#### `otlp` / `otlphttp`
Forwards telemetry to another Collector or backend via OTLP.

#### `prometheus`
Exposes a `/metrics` endpoint to be scraped by Prometheus.

#### `prometheusremotewrite`
Pushes metrics to a Prometheus-compatible remote-write endpoint.

#### `debug`
Prints telemetry payloads for local validation (demo/troubleshooting).

### Exporter configuration example
```yaml
exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"
  otlphttp:
    endpoint: "http://otel-backend:4318"
    tls:
      insecure: true
  debug:
    verbosity: detailed
```

---

## 8. Extensions (out-of-band capabilities)

**Extensions** are optional components that provide capabilities *not directly part of pipelines*.
They generally support the Collector runtime itself.

### Common extensions
- `health_check`: exposes a health endpoint for readiness/liveness probes.
- `pprof`: performance profiling endpoint.
- `zpages`: in-process diagnostic pages.
- `file_storage`: enables durable buffering for some exporters/processors.
- `memory_ballast` (legacy/less common now): heap tuning (often replaced by better runtime behavior).

Example:
```yaml
extensions:
  health_check:
  pprof:
    endpoint: 0.0.0.0:1777

service:
  extensions: [health_check, pprof]
```

---

## 9. Pipelines (the core wiring)

A **pipeline** defines the end-to-end path for a signal:

- which receivers ingest it,
- which processors run on it,
- which exporters deliver it.

Pipelines are defined under `service.pipelines` and are signal-specific:
- `traces`
- `metrics`
- `logs`

### Pipeline example (metrics)
```yaml
service:
  pipelines:
    metrics:
      receivers:  [hostmetrics]
      processors: [resource, batch]
      exporters:  [prometheus, debug]
```

### Key rules
- A pipeline must have at least one receiver and one exporter.
- A receiver/exporter/processor can be reused across pipelines.
- Pipelines are isolated by signal (metrics pipeline does not process traces unless you define a traces pipeline).

---

## 10. Full example: Host metrics to Prometheus + Debug (end-to-end)

```yaml
receivers:
  hostmetrics:
    collection_interval: 10s
    scrapers:
      cpu: {}
      memory: {}
      disk: {}
      filesystem: {}
      network: {}
      load: {}

processors:
  resource:
    attributes:
      - key: service.name
        value: "otelcol-hostmetrics-demo"
        action: upsert
      - key: deployment.environment
        value: "demo"
        action: upsert
  batch: {}

exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"
    resource_to_telemetry_conversion:
      enabled: true
  debug:
    verbosity: detailed

extensions:
  health_check: {}

service:
  extensions: [health_check]
  pipelines:
    metrics:
      receivers: [hostmetrics]
      processors: [resource, batch]
      exporters: [prometheus, debug]
```

How to validate:
- Prometheus scrape endpoint: `http://<collector-host>:8889/metrics`
- Debug exporter prints the payload in logs (useful for confirming attributes and metric names).

---

## 11. Operational considerations (production guidance)

### A) Cardinality management
High-cardinality labels/attributes can explode cost and memory usage.
Control via:
- `filter` (drop noisy series),
- `attributes/transform` (remove high-cardinality keys),
- enforce naming conventions.

### B) Batching and retries
- `batch` improves throughput.
- Exporters typically have retry logic; consider `sending_queue` features depending on exporter.

### C) Memory safety
Use:
- `memory_limiter`
- correct resource limits (Kubernetes)
- keep debug exporters out of production

### D) Multi-destination routing
You can export the same stream to multiple backends:
```yaml
exporters: [prometheus, otlphttp]
```

### E) Security
- Use TLS for OTLP exporters/receivers where possible.
- Avoid exposing debug endpoints publicly.
- Apply authentication at ingress (reverse proxies, service mesh) where appropriate.

---

## 12. Quick glossary

- **Receiver**: ingress component; how data enters the Collector.
- **Processor**: transforms/enriches/controls data in-flight.
- **Exporter**: egress component; how data leaves the Collector.
- **Extension**: runtime capability (health, profiling, storage).
- **Pipeline**: wiring of receiver(s) → processor(s) → exporter(s) for a signal.

---

## 13. Next steps (suggested learning path)

1. Start with OTLP receiver + debug exporter for traces/metrics validation.
2. Add resource enrichment (`resource` processor).
3. Add batching and memory safety (`batch`, `memory_limiter`).
4. Add vendor/backend exporters (OTLP, Prometheus, remote_write).
5. Add filters/transforms for governance and cost control.
6. Introduce tail sampling (for traces) only when you understand buffering and throughput.


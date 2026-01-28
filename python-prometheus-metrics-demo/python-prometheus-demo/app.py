import os
import time
from flask import Flask, request, jsonify, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

APP_NAME = os.getenv("APP_NAME", "python-metrics-demo")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv("APP_ENV", "local")

app = Flask(__name__)

# ---- Metrics ----
REQUESTS_TOTAL = Counter(
    "demo_requests_total",
    "Total HTTP requests",
    ["route", "method", "status"],
)

REQUEST_DURATION = Histogram(
    "demo_request_duration_seconds",
    "HTTP request latency (seconds)",
    ["route"],
    # sensible demo buckets (seconds)
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)

INPROGRESS = Gauge(
    "demo_inprogress_requests",
    "In-progress HTTP requests",
)

APP_INFO = Gauge(
    "demo_app_info",
    "Static app info (set to 1)",
    ["service", "version", "env"],
)
APP_INFO.labels(service=APP_NAME, version=APP_VERSION, env=APP_ENV).set(1)


def observe(route: str, start: float, status: int):
    duration = time.perf_counter() - start
    REQUESTS_TOTAL.labels(route=route, method=request.method, status=str(status)).inc()
    REQUEST_DURATION.labels(route=route).observe(duration)


@app.before_request
def _before():
    request._start_time = time.perf_counter()
    INPROGRESS.inc()


@app.after_request
def _after(resp):
    try:
        route = request.url_rule.rule if request.url_rule else "unknown"
    except Exception:
        route = "unknown"
    observe(route, request._start_time, resp.status_code)
    INPROGRESS.dec()
    return resp


@app.get("/")
def index():
    return jsonify(
        service=APP_NAME,
        version=APP_VERSION,
        env=APP_ENV,
        message="Hello! Hit /work?ms=200 to generate latency metrics. Visit /metrics for Prometheus.",
    )


@app.get("/work")
def work():
    # Simulated work (default 120ms), bounded for safety
    ms = int(request.args.get("ms", "120"))
    ms = max(0, min(ms, 5000))
    time.sleep(ms / 1000.0)
    return jsonify(ok=True, slept_ms=ms)


@app.get("/metrics")
def metrics():
    # Expose the default registry as Prometheus text format
    data = generate_latest()
    return Response(data, mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    # For local debugging without gunicorn (not used in Docker)
    app.run(host="0.0.0.0", port=8000)

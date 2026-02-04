from flask import Flask, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import random

app = Flask(__name__)

REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"]
)

REQ_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency in seconds",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5)
)

INFLIGHT = Gauge(
    "http_inflight_requests",
    "In-flight requests"
)

CPU_WORK_GAUGE = Gauge(
    "app_cpu_work_units",
    "Synthetic CPU work units (demo signal)"
)

@app.route("/work")
def work():
    INFLIGHT.inc()
    start = time.time()
    status = "200"

    # simulate variable latency + occasional errors
    latency = random.choice([0.01, 0.02, 0.05, 0.1, 0.2, 0.5])
    time.sleep(latency)

    # synthetic cpu work (no real cpu burn, just a changing signal)
    CPU_WORK_GAUGE.set(random.randint(1, 100))

    if random.random() < 0.05:
        status = "500"

    REQUESTS.labels("GET", "/work", status).inc()
    REQ_LATENCY.labels("GET", "/work").observe(time.time() - start)
    INFLIGHT.dec()

    return ("ok" if status == "200" else "error"), int(status)

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/")
def home():
    return "Hello. Try /work and /metrics"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

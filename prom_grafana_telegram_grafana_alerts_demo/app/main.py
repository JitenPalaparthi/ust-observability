from flask import Flask, Response, request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

REQUESTS = Counter("demo_requests_total", "Total HTTP requests", ["path", "method", "code"])
ERRORS = Counter("demo_errors_total", "Total simulated errors")

@app.after_request
def _record_metrics(resp):
    try:
        REQUESTS.labels(path=request.path, method=request.method, code=str(resp.status_code)).inc()
    except Exception:
        pass
    return resp

@app.get("/")
def index():
    return {
        "ok": True,
        "message": "Prometheus metrics demo app for Grafana Alerting → Telegram",
        "endpoints": ["/metrics", "/trigger-error", "/healthz"]
    }

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/trigger-error")
def trigger_error():
    ERRORS.inc()
    return {"ok": True, "errors_total": "incremented"}

@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(data, mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

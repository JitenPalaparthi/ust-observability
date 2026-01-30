import os
import time
import logging

import requests
from flask import Flask, jsonify

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


# ---------- Config ----------
PORT = int(os.getenv("PORT", "8000"))
LOG_FILE = os.getenv("LOG_FILE", "/var/log/app/app.log")

JAEGER_HOST = os.getenv("OTEL_EXPORTER_JAEGER_AGENT_HOST", "jaeger")
JAEGER_PORT = int(os.getenv("OTEL_EXPORTER_JAEGER_AGENT_PORT", "6831"))

SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "py-app")


# ---------- Logging ----------
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s level=%(levelname)s service=py-app msg=%(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger("py-app")


# ---------- Metrics ----------
REQUESTS = Counter("app_requests_total", "Total HTTP requests", ["path", "status"])
LATENCY = Histogram("app_request_latency_seconds", "Request latency", ["path"])


# ---------- Tracing (Jaeger Agent UDP 6831) ----------
resource = Resource.create({"service.name": SERVICE_NAME})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

jaeger_exporter = JaegerExporter(
    agent_host_name=JAEGER_HOST,
    agent_port=JAEGER_PORT,
)

provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
tracer = trace.get_tracer("py-app")


# ---------- Flask ----------
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


@app.get("/")
def root():
    start = time.time()
    status = 200
    try:
        logger.info("handling /")

        # generate a child span + outgoing HTTP call span (requests instrumentation)
        with tracer.start_as_current_span("call-httpbin"):
            requests.get("https://httpbin.org/get", timeout=2)

        return jsonify({"ok": True, "msg": "metrics+logs+traces"})
    except Exception as e:
        status = 500
        logger.exception(f"error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        LATENCY.labels(path="/").observe(time.time() - start)
        REQUESTS.labels(path="/", status=str(status)).inc()


@app.get("/work")
def work():
    start = time.time()
    status = 200
    try:
        logger.info("handling /work")
        with tracer.start_as_current_span("cpu-work"):
            x = 0
            for i in range(250_000):
                x += i
        return jsonify({"ok": True, "result": x})
    except Exception as e:
        status = 500
        logger.exception(f"error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        LATENCY.labels(path="/work").observe(time.time() - start)
        REQUESTS.labels(path="/work", status=str(status)).inc()


@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    logger.info(f"starting on 0.0.0.0:{PORT}, jaeger={JAEGER_HOST}:{JAEGER_PORT}")
    app.run(host="0.0.0.0", port=PORT)
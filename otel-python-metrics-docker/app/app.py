import os
import time
import random
import logging

from opentelemetry import metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter


def setup_logging():
    level = os.getenv("APP_LOG_LEVEL", "DEBUG").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def setup_metrics():
    # When running in docker-compose, 'collector' is the service DNS name.
    otlp_endpoint = os.getenv(
        "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
        "http://collector:4318/v1/metrics",
    )

    resource = Resource.create({
        "service.name": os.getenv("OTEL_SERVICE_NAME", "python-metrics-demo"),
        "service.version": "1.0.0",
        "deployment.environment": os.getenv("ENV", "local"),
    })

    exporter = OTLPMetricExporter(endpoint=otlp_endpoint)

    readers = [
        PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
    ]

    # Optional: also print exported metrics to container logs (debug)
    if os.getenv("METRICS_CONSOLE_DEBUG", "true").lower() == "true":
        readers.append(
            PeriodicExportingMetricReader(
                ConsoleMetricExporter(),
                export_interval_millis=5000,
            )
        )

    provider = MeterProvider(resource=resource, metric_readers=readers)
    metrics.set_meter_provider(provider)
    return metrics.get_meter("demo.meter")


def main():
    setup_logging()
    log = logging.getLogger("app")

    meter = setup_metrics()

    counter = meter.create_counter(
        "demo_requests_total",
        description="Total demo requests",
    )

    histogram = meter.create_histogram(
        "demo_request_latency_ms",
        description="Request latency",
        unit="ms",
    )

    queue_depth = 0

    def observe_queue(_options):
        return [metrics.Observation(queue_depth, {"queue": "main"})]

    meter.create_observable_gauge(
        "demo_queue_depth",
        callbacks=[observe_queue],
        description="Queue depth",
    )

    log.info("Starting metric emission. OTLP endpoint=%s", os.getenv("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT", "http://collector:4318/v1/metrics"))

    while True:
        route = random.choice(["/home", "/api", "/health"])
        status = random.choice(["200", "200", "200", "500"])
        latency = random.randint(5, 400)

        queue_depth = max(0, queue_depth + random.randint(-2, 3))

        attrs = {"route": route, "status": status}

        counter.add(1, attrs)
        histogram.record(latency, attrs)

        log.debug("route=%s status=%s latency=%d queue=%d", route, status, latency, queue_depth)
        time.sleep(1)


if __name__ == "__main__":
    main()

import os
import time
import logging

from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource


def setup_otel_logging():
    service_name = os.getenv("OTEL_SERVICE_NAME", "python-otel-logs-demo")

    # Build resource attributes (includes Loki label-hints)
    resource_attrs = {
        "service.name": service_name,
        "service.environment": "dev",

        # IMPORTANT: Loki exporter uses these hint attributes to promote selected
        # attributes to Loki labels (supported by the upstream loki exporter).
        # This avoids relying on deprecated exporter-side label mapping.
        "loki.resource.labels": "service.name,service.environment",

        # Optional: if you want log attributes to become labels too, list them here.
        # Keep label cardinality low.
        "loki.attribute.labels": "custom_key",
    }

    resource = Resource.create(resource_attrs)

    logger_provider = LoggerProvider(resource=resource)
    _logs.set_logger_provider(logger_provider)

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT", "http://otel-collector:4318/v1/logs")
    exporter = OTLPLogExporter(endpoint=endpoint)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

    # Bridge stdlib logging → OTel Logs
    handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)

    root_logger = logging.getLogger()
    root_logger.setLevel(os.getenv("APP_LOG_LEVEL", "INFO").upper())
    root_logger.addHandler(handler)

    # Also print logs to console
    console = logging.StreamHandler()
    console.setLevel(root_logger.level)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    console.setFormatter(fmt)
    root_logger.addHandler(console)


def main():
    setup_otel_logging()
    log = logging.getLogger("demo-app")

    log.info("Python OTEL logs demo started")
    i = 0
    while True:
        # custom_key becomes a Loki label because it's listed in loki.attribute.labels
        log.info("Example log line from Python app", extra={"iteration": i, "custom_key": "demo"})
        time.sleep(2)
        i += 1


if __name__ == "__main__":
    main()

import logging
import time

from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.resources import SERVICE_NAME


def setup_logging():
    # 1) Define resource (service metadata)
    resource = Resource.create({
        SERVICE_NAME: "python-otel-logs-demo",
        "service.environment": "dev",
    })

    # 2) Create LoggerProvider and set global
    logger_provider = LoggerProvider(resource=resource)
    _logs.set_logger_provider(logger_provider)

    # 3) Create OTLP Log Exporter pointing to OTel Collector
    exporter = OTLPLogExporter(
        endpoint="http://otel-collector:4318/v1/logs",
        insecure=True,
    )

    # 4) Add batch processor
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(exporter)
    )

    # 5) Bridge Python logging to OpenTelemetry
    handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    # Optional: also log to console for local visibility
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)


def main():
    setup_logging()
    logger = logging.getLogger("demo-app")

    i = 0
    logger.info("Python OpenTelemetry logging demo started")
    while True:
        logger.info(
            "Example log from Python application",
            extra={
                "custom_key": "custom_value",
                "iteration": i,
            },
        )
        time.sleep(2)
        i += 1


if __name__ == "__main__":
    main()

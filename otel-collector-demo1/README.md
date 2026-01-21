docker run --rm -it \
  -p 8889:8889 \
  -v "$(pwd)/otelcol.yaml:/etc/otelcol-contrib/config.yaml" \
  otel/opentelemetry-collector-contrib:latest
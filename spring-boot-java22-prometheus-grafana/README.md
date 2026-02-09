# Spring Boot (Java 22) + Prometheus + Grafana (Provisioned Dashboards)

This is a **docker-compose** based example:
- Spring Boot app exposes metrics at **/actuator/prometheus**
- Prometheus scrapes the app
- Grafana auto-provisions:
  - Prometheus datasource
  - A starter dashboard under folder **Spring Boot**

## Prereqs
- Java **22** installed (only if you want to run without Docker)
- Docker + Docker Compose

## Quick start (recommended)
```bash
docker compose up --build
```

### URLs
- App: http://localhost:8080/api/hello?name=JP&workMs=50
- Actuator: http://localhost:8080/actuator
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000  (user: **admin**, pass: **admin**)

## Generate some traffic
```bash
# Run this a few times to see graphs move
curl "http://localhost:8080/api/hello?name=JP&workMs=30"
```

## Run app locally (without Docker)
```bash
mvn spring-boot:run
```
Then run only Prometheus+Grafana:
```bash
docker compose up prometheus grafana
```

## Notes
- The dashboard uses common Micrometer Prometheus metric names such as:
  - `http_server_requests_seconds_*`
  - `jvm_memory_*`
  - `process_cpu_usage`, `system_cpu_usage`
- You can import additional community dashboards if you want (e.g. JVM Micrometer dashboards on Grafana.com).

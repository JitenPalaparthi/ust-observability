import json
import requests

GRAFANA_URL = "http://localhost:3000"
TOKEN = "PASTE_YOUR_GRAFANA_TOKEN_HERE"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def post(path, payload):
    r = requests.post(f"{GRAFANA_URL}{path}", headers=HEADERS, data=json.dumps(payload))
    if r.status_code >= 300:
        raise RuntimeError(f"{path} failed: {r.status_code} {r.text}")
    return r.json()

def create_prometheus_datasource():
    payload = {
        "name": "Prometheus",
        "type": "prometheus",
        "url": "http://prometheus:9090",
        "access": "proxy",
        "isDefault": True
    }
    try:
        print(post("/api/datasources", payload))
    except RuntimeError as e:
        # datasource may already exist; ignore if so
        print("Datasource create note:", e)

def import_dashboard(dashboard_json_path, folder_id=0):
    with open(dashboard_json_path, "r", encoding="utf-8") as f:
        dashboard = json.load(f)

    payload = {"dashboard": dashboard, "folderId": folder_id, "overwrite": True}
    print(post("/api/dashboards/db", payload))

if __name__ == "__main__":
    create_prometheus_datasource()
    import_dashboard("grafana/dashboards/python_service_overview.json")
    import_dashboard("grafana/dashboards/python_service_errors_latency.json")
    import_dashboard("grafana/dashboards/prometheus_self_basic.json")

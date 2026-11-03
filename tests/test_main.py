import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.reliability import reliability_service


@pytest.fixture
def client():
    # Ensure clean readiness before each test
    reliability_service.set_readiness(True)
    reliability_service.set_latency_simulation(0.0)
    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "service" in data


def test_health_liveness_probe(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pass"
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0


def test_ready_probe_when_ready(client):
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["ready"] is True


def test_ready_probe_when_unready(client):
    # Toggle readiness to False
    toggle_resp = client.post("/chaos/toggle-readiness", json={"ready": False})
    assert toggle_resp.status_code == 200

    # Probe should return 503 Service Unavailable
    response = client.get("/ready")
    assert response.status_code == 503
    assert "Service is not ready" in response.json()["detail"]

    # Restore readiness
    restore_resp = client.post("/chaos/toggle-readiness", json={"ready": True})
    assert restore_resp.status_code == 200
    assert client.get("/ready").status_code == 200


def test_metrics_scrape_endpoint(client):
    # Make a few requests to populate metrics
    client.get("/")
    client.get("/health")

    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    body = response.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body


def test_chaos_simulated_error(client):
    response = client.get("/chaos/error")
    assert response.status_code == 500
    assert "Simulated internal server error" in response.json()["detail"]


def test_not_found_endpoint_records_metric(client):
    response = client.get("/non-existent-route-404")
    assert response.status_code == 404

    # Verify 404 is registered in metrics
    metrics_response = client.get("/metrics")
    assert 'status_code="404"' in metrics_response.text

from fastapi.testclient import TestClient

from app.main import app


def test_root_returns_application_metadata() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "Anithium Social Agent"
    assert response.json()["status"] == "running"


def test_liveness_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

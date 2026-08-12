from fastapi.testclient import TestClient

from app import __version__
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "up", "version": __version__}


def test_submit_normal_reading():
    response = client.post(
        "/readings",
        json={"pump_id": "P-201", "temperature_c": 70, "vibration_mm_s": 2.5, "pressure_bar": 8.0},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_submit_critical_reading():
    response = client.post(
        "/readings",
        json={"pump_id": "P-201", "temperature_c": 99, "vibration_mm_s": 9.0, "pressure_bar": 8.0},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "critical"


def test_dashboard_shows_version():
    response = client.get("/")
    assert response.status_code == 200
    assert __version__ in response.text


def test_invalid_reading_rejected():
    response = client.post("/readings", json={"pump_id": "P-201"})
    assert response.status_code == 422

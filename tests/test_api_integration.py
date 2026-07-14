import requests


BASE_URL = "http://127.0.0.1:5000"


def test_health_endpoint():
    response = requests.get(
        f"{BASE_URL}/api/health",
        timeout=10,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["message"] == "API is running successfully"


def test_database_health_endpoint():
    response = requests.get(
        f"{BASE_URL}/api/database-health",
        timeout=15,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["message"] == "MongoDB Atlas connection successful"


def test_events_endpoint_returns_json():
    response = requests.get(
        f"{BASE_URL}/api/events",
        timeout=15,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "count" in data
    assert "events" in data
    assert isinstance(data["events"], list)
from app import app


def test_index_returns_application_information():
    client = app.test_client()
    response = client.get("/")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["application"] == "JensenStore API"
    assert payload["version"] == "1.0.0"


def test_health_returns_healthy():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


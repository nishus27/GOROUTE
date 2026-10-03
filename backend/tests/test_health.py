"""Health endpoint tests."""


def test_health_returns_ok(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "service": "goroute"}


def test_unknown_route_returns_json_error(client):
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    body = response.get_json()
    assert "error" in body

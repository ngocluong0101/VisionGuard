def test_root_returns_basic_project_info(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["app"] == "VisionGuard"
    assert response.json()["status"] == "ok"


def test_health_returns_ok(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "ok"
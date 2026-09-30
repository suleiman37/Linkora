from fastapi.testclient import TestClient

from app.main import app


def test_request_id_is_generated_on_success() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.headers["x-request-id"].startswith("req_")


def test_valid_request_id_is_preserved() -> None:
    request_id = "client-request-123"

    response = TestClient(app).get(
        "/health",
        headers={"X-Request-ID": request_id},
    )

    assert response.headers["x-request-id"] == request_id


def test_invalid_request_id_is_replaced() -> None:
    response = TestClient(app).get(
        "/health",
        headers={"X-Request-ID": "bad\nrequest"},
    )

    assert response.headers["x-request-id"].startswith("req_")


def test_validation_error_uses_error_envelope() -> None:
    response = TestClient(app).post("/api/v1/links", json={"url": "ftp://example.com"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]
    assert response.json()["error"]["details"]


def test_unknown_route_uses_error_envelope() -> None:
    response = TestClient(app).get("/api/v1/route-that-does-not-exist")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "http_error"
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]


def test_frontend_origin_is_allowed_by_cors() -> None:
    response = TestClient(app).options(
        "/api/v1/links",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
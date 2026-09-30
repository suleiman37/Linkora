from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.database import get_db
from app.main import app
from app.models import Link
from app.services.links import LinkCreationError, LinkService
from app.utils.urls import normalize_url


def test_create_link_persists_record(isolated_session_factory: sessionmaker[Session], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BASE_URL", "http://localhost:8000")

    def override_get_db() -> Iterator[Session]:
        with isolated_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).post(
            "/api/v1/links",
            json={"url": "https://example.com/article?id=123#section"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["original_url"] == "https://example.com/article?id=123#section"
    assert body["short_url"].startswith("http://localhost:8000/")
    assert len(body["short_code"]) == 7

    with isolated_session_factory() as session:
        link = session.scalar(select(Link).where(Link.id == body["id"]))
        assert link is not None
        assert link.original_url == body["original_url"]
        assert link.normalized_url == "https://example.com/article?id=123#section"


def test_normalized_url_database_constraint_rejects_duplicates(
    isolated_session_factory: sessionmaker[Session],
) -> None:
    with isolated_session_factory() as session:
        session.add(
            Link(
                original_url="https://example.com/one",
                normalized_url="https://example.com/one",
                short_code="fixed01",
            )
        )
        session.commit()
        session.add(
            Link(
                original_url="HTTPS://Example.com/one",
                normalized_url="https://example.com/one",
                short_code="fixed02",
            )
        )

        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


def test_short_code_redirects_to_original_url(
    isolated_session_factory: sessionmaker[Session],
) -> None:
    def override_get_db() -> Iterator[Session]:
        with isolated_session_factory() as session:
            yield session

    with isolated_session_factory() as session:
        session.add(
            Link(
                original_url="https://example.com/redirect?source=test#section",
                normalized_url=normalize_url("https://example.com/redirect?source=test#section"),
                short_code="fixed01",
            )
        )
        session.commit()

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).get("/fixed01", follow_redirects=False)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/redirect?source=test#section"

    with isolated_session_factory() as session:
        link = session.scalar(select(Link).where(Link.short_code == "fixed01"))
        assert link is not None
        assert link.click_count == 1
        assert link.last_clicked_at is not None


def test_statistics_endpoint_returns_counts_without_incrementing(
    isolated_session_factory: sessionmaker[Session],
) -> None:
    def override_get_db() -> Iterator[Session]:
        with isolated_session_factory() as session:
            yield session

    with isolated_session_factory() as session:
        session.add(
            Link(
                original_url="https://example.com/stats",
                normalized_url=normalize_url("https://example.com/stats"),
                short_code="stats01",
            )
        )
        session.commit()

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).get("/api/v1/links/stats01/stats")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["short_code"] == "stats01"
    assert response.json()["click_count"] == 0
    assert response.json()["last_clicked_at"] is None


def test_missing_statistics_returns_not_found(
    isolated_session_factory: sessionmaker[Session],
) -> None:
    def override_get_db() -> Iterator[Session]:
        with isolated_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).get("/api/v1/links/missing01/stats")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "link_not_found"
    assert response.json()["error"]["message"] == "Link not found"
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]


def test_missing_redirect_does_not_create_statistics(
    isolated_session_factory: sessionmaker[Session],
) -> None:
    def override_get_db() -> Iterator[Session]:
        with isolated_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).get("/missing01", follow_redirects=False)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    with isolated_session_factory() as session:
        assert session.query(Link).count() == 0


def test_missing_short_code_returns_not_found(isolated_session_factory: sessionmaker[Session]) -> None:
    def override_get_db() -> Iterator[Session]:
        with isolated_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).get("/missing01", follow_redirects=False)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "link_not_found"
    assert response.json()["error"]["message"] == "Link not found"
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]


def test_equivalent_url_reuses_existing_link(
    isolated_session_factory: sessionmaker[Session],
) -> None:
    def override_get_db() -> Iterator[Session]:
        with isolated_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        client = TestClient(app)
        first_response = client.post(
            "/api/v1/links",
            json={"url": "HTTPS://Example.com/article"},
        )
        second_response = client.post(
            "/api/v1/links",
            json={"url": "https://example.com/article"},
        )
    finally:
        app.dependency_overrides.clear()

    assert first_response.status_code == 201
    assert first_response.headers["x-link-existing"] == "false"
    assert second_response.status_code == 200
    assert second_response.headers["x-link-existing"] == "true"
    assert second_response.json()["id"] == first_response.json()["id"]
    assert second_response.json()["short_code"] == first_response.json()["short_code"]

    with isolated_session_factory() as session:
        assert session.query(Link).count() == 1


@pytest.mark.parametrize(
    ("original", "normalized"),
    [
        (
            "HTTP://Example.com:80/article",
            "http://example.com/article",
        ),
        (
            "https://Example.com:443/article?a=1&b=2#section",
            "https://example.com/article?a=1&b=2#section",
        ),
        (
            "https://example.com/article/",
            "https://example.com/article/",
        ),
    ],
)
def test_normalize_url_is_conservative(original: str, normalized: str) -> None:
    assert normalize_url(original) == normalized


def test_link_service_retries_short_code_collision(isolated_session_factory: sessionmaker[Session]) -> None:
    with isolated_session_factory() as session:
        session.add(
            Link(
                original_url="https://existing.example",
                normalized_url=normalize_url("https://existing.example"),
                short_code="fixed01",
            )
        )
        session.commit()

        generated_codes = iter(["fixed01", "fixed02"])
        link = LinkService(code_generator=lambda: next(generated_codes)).create_link(
            session,
            "https://new.example",
        )

        assert link.short_code == "fixed02"


def test_link_service_does_not_retry_other_integrity_errors(
    isolated_session_factory: sessionmaker[Session],
) -> None:
    with isolated_session_factory() as session:
        generated_codes = iter(["fixed01", "fixed02"])
        session.add(
            Link(
                original_url="https://existing.example",
                normalized_url=normalize_url("https://existing.example"),
                short_code="fixed01",
            )
        )
        session.commit()

        original_add = LinkService().repository.add

        def failing_add(database_session: Session, link: Link) -> None:
            raise IntegrityError("insert", {}, Exception("other constraint"))

        service = LinkService(
            code_generator=lambda: next(generated_codes),
        )
        service.repository.add = failing_add

        with pytest.raises(LinkCreationError, match="Unable to create link"):
            service.create_link(session, "https://new.example")

        service.repository.add = original_add


@pytest.mark.parametrize(
    "url",
    [
        "",
        " example.com ",
        "ftp://example.com/file",
        "javascript:alert(1)",
        "https://user:password@example.com",
        "https:///missing-host",
    ],
)
def test_create_link_rejects_invalid_urls(url: str) -> None:
    response = TestClient(app).post("/api/v1/links", json={"url": url})

    assert response.status_code == 422
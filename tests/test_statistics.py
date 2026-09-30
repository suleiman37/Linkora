from collections.abc import Iterator

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.database import get_db
from app.main import app
from app.models import Link
from app.utils.urls import normalize_url


def test_two_redirects_increment_click_count(
    isolated_session_factory: sessionmaker[Session],
) -> None:
    def override_get_db() -> Iterator[Session]:
        with isolated_session_factory() as session:
            yield session

    with isolated_session_factory() as session:
        session.add(
            Link(
                original_url="https://example.com/two-clicks",
                normalized_url=normalize_url("https://example.com/two-clicks"),
                short_code="twoclk1",
            )
        )
        session.commit()

    app.dependency_overrides[get_db] = override_get_db
    try:
        client = TestClient(app)
        first = client.get("/twoclk1", follow_redirects=False)
        second = client.get("/twoclk1", follow_redirects=False)
    finally:
        app.dependency_overrides.clear()

    assert first.status_code == 302
    assert second.status_code == 302
    with isolated_session_factory() as session:
        link = session.scalar(select(Link).where(Link.short_code == "twoclk1"))
        assert link is not None
        assert link.click_count == 2
        assert link.last_clicked_at is not None


def test_statistics_read_does_not_increment(
    isolated_session_factory: sessionmaker[Session],
) -> None:
    def override_get_db() -> Iterator[Session]:
        with isolated_session_factory() as session:
            yield session

    with isolated_session_factory() as session:
        session.add(
            Link(
                original_url="https://example.com/read-only",
                normalized_url=normalize_url("https://example.com/read-only"),
                short_code="readonly",
            )
        )
        session.commit()

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).get("/api/v1/links/readonly/stats")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["click_count"] == 0


def test_analytics_summary_returns_empty_workspace(
    isolated_session_factory: sessionmaker[Session],
) -> None:
    def override_get_db() -> Iterator[Session]:
        with isolated_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).get("/api/v1/analytics/summary")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "total_links": 0,
        "total_clicks": 0,
        "last_clicked_at": None,
        "top_links": [],
        "recently_active_links": [],
    }


def test_analytics_summary_returns_totals_and_rankings(
    isolated_session_factory: sessionmaker[Session],
) -> None:
    def override_get_db() -> Iterator[Session]:
        with isolated_session_factory() as session:
            yield session

    with isolated_session_factory() as session:
        session.add_all(
            [
                Link(
                    original_url="https://example.com/most-clicked",
                    normalized_url=normalize_url("https://example.com/most-clicked"),
                    short_code="most001",
                    click_count=4,
                ),
                Link(
                    original_url="https://example.com/recent",
                    normalized_url=normalize_url("https://example.com/recent"),
                    short_code="recent1",
                    click_count=2,
                ),
                Link(
                    original_url="https://example.com/new",
                    normalized_url=normalize_url("https://example.com/new"),
                    short_code="new0001",
                ),
            ]
        )
        session.commit()

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).get("/api/v1/analytics/summary")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["total_links"] == 3
    assert body["total_clicks"] == 6
    assert body["last_clicked_at"] is None
    assert [link["short_code"] for link in body["top_links"]] == ["most001", "recent1", "new0001"]
    assert body["recently_active_links"] == []
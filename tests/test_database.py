import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import Mock

from app.config import Settings
from app.database import DatabaseConnectionError, verify_database_connection


def test_settings_use_database_url_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://test:test@localhost:5432/test_db",
    )

    settings = Settings()

    assert settings.database_url.endswith("/test_db")


def test_verify_database_connection_works_with_sqlite() -> None:
    sqlite_engine = create_engine("sqlite://")

    verify_database_connection(sqlite_engine)


def test_verify_database_connection_raises_clear_error() -> None:
    unavailable_engine = Mock()
    unavailable_engine.connect.side_effect = SQLAlchemyError("connection failed")

    with pytest.raises(DatabaseConnectionError, match="Unable to connect"):
        verify_database_connection(unavailable_engine)
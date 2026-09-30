from collections.abc import Generator

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings
from app.errors.exceptions import ApplicationError


class DatabaseConnectionError(ApplicationError):
    """Raised when the application cannot connect to the configured database."""

    status_code = 503
    error_code = "database_unavailable"
    default_message = "Database unavailable"


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_database_connection(database_engine: Engine = engine) -> None:
    try:
        with database_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise DatabaseConnectionError(
            "Unable to connect to the configured database."
        ) from error
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.models import Link
from app.services.links import LinkService
from app.utils.urls import normalize_url


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="Set TEST_DATABASE_URL to run PostgreSQL integration tests",
)
def test_concurrent_clicks_are_atomic() -> None:
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    short_code = f"{uuid4().hex[:6]}a"
    link_id: int | None = None
    try:
        with factory() as session:
            link = Link(
                original_url="https://example.com/concurrent",
                normalized_url=normalize_url("https://example.com/concurrent"),
                short_code=short_code,
            )
            session.add(link)
            session.commit()
            link_id = link.id

        barrier = Barrier(10)

        def record_click() -> None:
            with factory() as session:
                barrier.wait()
                LinkService().resolve_and_record_click(session, short_code)

        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(lambda _: record_click(), range(10)))

        with factory() as session:
            link = session.scalar(select(Link).where(Link.id == link_id))
            assert link is not None
            assert link.click_count == 10
            assert link.last_clicked_at is not None
    finally:
        if link_id is not None:
            with factory() as session:
                session.query(Link).filter(Link.id == link_id).delete()
                session.commit()
        engine.dispose()
"""add normalized URL for duplicate handling

Revision ID: 0002_add_normalized_url
Revises: 0001_create_links
"""
from alembic import op
import sqlalchemy as sa

from app.utils.urls import normalize_url


revision = "0002_add_normalized_url"
down_revision = "0001_create_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("links", sa.Column("normalized_url", sa.Text(), nullable=True))
    connection = op.get_bind()
    rows = connection.execute(sa.text("SELECT id, original_url FROM links")).mappings()
    normalized_ids: dict[str, list[int]] = {}
    for row in rows:
        normalized_url = normalize_url(row["original_url"])
        normalized_ids.setdefault(normalized_url, []).append(row["id"])
        connection.execute(
            sa.text("UPDATE links SET normalized_url = :normalized_url WHERE id = :id"),
            {"id": row["id"], "normalized_url": normalized_url},
        )
    collisions = {
        normalized_url: ids
        for normalized_url, ids in normalized_ids.items()
        if len(ids) > 1
    }
    if collisions:
        details = "; ".join(
            f"{normalized_url}: link IDs {ids}"
            for normalized_url, ids in collisions.items()
        )
        raise RuntimeError(
            "Cannot add unique normalized_url constraint; resolve existing "
            f"duplicate links first ({details})."
        )
    op.alter_column("links", "normalized_url", nullable=False)
    op.create_unique_constraint(
        "uq_links_normalized_url",
        "links",
        ["normalized_url"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_links_normalized_url", "links", type_="unique")
    op.drop_column("links", "normalized_url")
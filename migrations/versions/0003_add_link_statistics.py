"""add aggregate link statistics

Revision ID: 0003_add_link_statistics
Revises: 0002_add_normalized_url
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_add_link_statistics"
down_revision = "0002_add_normalized_url"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "links",
        sa.Column(
            "click_count",
            sa.BigInteger(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.add_column(
        "links",
        sa.Column("last_clicked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_check_constraint(
        "ck_links_click_count_nonnegative",
        "links",
        "click_count >= 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_links_click_count_nonnegative", "links", type_="check")
    op.drop_column("links", "last_clicked_at")
    op.drop_column("links", "click_count")
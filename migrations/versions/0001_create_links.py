"""create links table

Revision ID: 0001_create_links
Revises:
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_create_links"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "links",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("original_url", sa.Text(), nullable=False),
        sa.Column("short_code", sa.String(length=7), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("short_code", name="uq_links_short_code"),
    )


def downgrade() -> None:
    op.drop_table("links")